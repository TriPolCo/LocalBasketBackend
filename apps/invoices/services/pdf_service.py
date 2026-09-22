from io import BytesIO

import qrcode

from django.conf import settings

from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.invoices.models.invoice import Invoice


class InvoicePDFService:
    # Clean monochromatic palette typical of shipping labels
    PRIMARY_COLOR = colors.black
    BORDER_COLOR = colors.black
    BG_LIGHT = colors.HexColor("#f1f5f9")  # Very light grey container tint
    TEXT_DARK = colors.HexColor("#0f172a")

    @staticmethod
    def _create_qr_image(invoice):
        base_url = getattr(
            settings,
            "PUBLIC_BASE_URL",
            "http://127.0.0.1:8000",
        )

        qr_url = (
            f"{base_url.rstrip('/')}"
            f"/api/v1/invoices/delivery/verify/"
            f"{invoice.qr_token}/"
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=1,
        )

        qr.add_data(qr_url)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)

        return Image(
            buffer,
            width=24 * mm,
            height=24 * mm,
        )

    @staticmethod
    def _create_barcode(order_number):
        return createBarcodeDrawing(
            "Code128",
            value=order_number,
            barHeight=10 * mm,
            barWidth=0.4,
            humanReadable=True,
        )

    @staticmethod
    def _money(value):
        if value is None:
            return "Rs. 0.00"
        return f"Rs. {value:,.2f}"

    @staticmethod
    def generate(invoice):
        order = invoice.order
        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
            title=f"DailyDrops - {order.order_number}",
            author="DailyDrops",
        )

        styles = getSampleStyleSheet()

        normal_style = ParagraphStyle(
            "NormalCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=InvoicePDFService.TEXT_DARK,
        )

        bold_style = ParagraphStyle(
            "BoldCustom",
            parent=normal_style,
            fontName="Helvetica-Bold",
        )

        brand_style = ParagraphStyle(
            "Brand",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            alignment=TA_LEFT,
            textColor=colors.black,
        )

        right_style = ParagraphStyle(
            "Right",
            parent=normal_style,
            alignment=TA_RIGHT,
        )

        center_style = ParagraphStyle(
            "Center",
            parent=normal_style,
            alignment=TA_CENTER,
        )

        th_style = ParagraphStyle(
            "TH",
            parent=bold_style,
            textColor=colors.white,
        )

        th_center = ParagraphStyle(
            "THCenter",
            parent=center_style,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        th_right = ParagraphStyle(
            "THRight",
            parent=right_style,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        story = []

        # ---------------------------------------------------------
        # TOP BANNER: BRAND & LOGISTICS HEADER
        # ---------------------------------------------------------
        barcode = InvoicePDFService._create_barcode(order.order_number)

        brand_meta_data = [
            [
                Paragraph("<b>DAILYDROPS EXPRESS</b>", brand_style),
                Paragraph(
                    f"<b>Invoice:</b> {invoice.invoice_number}<br/><b>Date:</b> {order.created_at.strftime('%d %b %Y')}",
                    right_style)
            ],
            [
                Paragraph(f"<b>Order ID:</b> {order.order_number}", bold_style),
                barcode
            ]
        ]

        brand_table = Table(brand_meta_data, colWidths=[90 * mm, 100 * mm])
        brand_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("BACKGROUND", (0, 0), (-1, -1), InvoicePDFService.BG_LIGHT),
                ]
            )
        )
        story.append(brand_table)
        story.append(Spacer(1, 3 * mm))

        # ---------------------------------------------------------
        # SHIPPING ADDRESS & PAYMENT BLOCK (Flipkart Split-Pane)
        # ---------------------------------------------------------
        address_parts = [order.shipping_address_line_1]
        if order.shipping_address_line_2:
            address_parts.append(order.shipping_address_line_2)
        if order.shipping_landmark:
            address_parts.append(f"Landmark: {order.shipping_landmark}")
        address_parts.append(f"<b>{order.shipping_city}, {order.shipping_state} - {order.shipping_postal_code}</b>")
        address_parts.append(order.shipping_country)
        address_text = "<br/>".join(address_parts)

        shipping_data = [
            [
                Paragraph("<b>SHIPPING ADDRESS (DELIVER TO)</b>", th_style),
                Paragraph("<b>PAYMENT SUMMARY</b>", th_style),
            ],
            [
                Paragraph(
                    f"<b>{order.shipping_full_name}</b><br/>"
                    f"{address_text}<br/><br/>"
                    f"<b>Phone:</b> {order.shipping_phone_number}",
                    normal_style,
                ),
                Paragraph(
                    f"<b>Method:</b> {order.payment_method}<br/>"
                    f"<b>Status:</b> {order.payment_status}<br/>"
                    f"<b>Total:</b> {InvoicePDFService._money(order.total_amount)}<br/>"
                    f"<b>To Collect:</b> <font size=10><b>{InvoicePDFService._money(order.total_amount if order.payment_status != 'PAID' else 0)}</b></font>",
                    normal_style,
                ),
            ],
        ]

        shipping_table = Table(shipping_data, colWidths=[120 * mm, 70 * mm])
        shipping_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(shipping_table)
        story.append(Spacer(1, 3 * mm))

        # ---------------------------------------------------------
        # ITEM MANIFEST TABLE (Condensed Flipkart Style)
        # ---------------------------------------------------------
        item_rows = [
            [
                Paragraph("<b>#</b>", th_center),
                Paragraph("<b>ITEM DESCRIPTION</b>", th_style),
                Paragraph("<b>QTY</b>", th_center),
                Paragraph("<b>PRICE</b>", th_right),
                Paragraph("<b>TOTAL</b>", th_right),
            ]
        ]

        for index, item in enumerate(order.items.all(), start=1):
            item_rows.append(
                [
                    Paragraph(str(index), center_style),
                    Paragraph(f"<b>{item.product_name}</b>", normal_style),
                    Paragraph(str(item.quantity), center_style),
                    Paragraph(InvoicePDFService._money(item.selling_price), right_style),
                    Paragraph(InvoicePDFService._money(item.item_total), right_style),
                ]
            )

        item_table = Table(
            item_rows,
            colWidths=[8 * mm, 112 * mm, 14 * mm, 28 * mm, 28 * mm],
            repeatRows=1,
        )
        item_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(item_table)
        story.append(Spacer(1, 3 * mm))

        # ---------------------------------------------------------
        # QR CODE & AGENT SCAN PANEL
        # ---------------------------------------------------------
        qr_image = InvoicePDFService._create_qr_image(invoice)

        scan_info = Paragraph(
            "<b>LOGISTICS VERIFICATION QR</b><br/>"
            "Delivery executives must scan this code via the internal app upon delivery completion. "
            "Do not accept returns if seal is broken.",
            normal_style,
        )

        qr_section_data = [
            [
                qr_image,
                scan_info,
                Paragraph(f"<b>Status:</b> {order.status}<br/><b>Hub:</b> Direct Dispatch", right_style)
            ]
        ]

        qr_section = Table(qr_section_data, colWidths=[30 * mm, 110 * mm, 50 * mm])
        qr_section.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("BACKGROUND", (0, 0), (-1, -1), InvoicePDFService.BG_LIGHT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )

        story.append(KeepTogether(qr_section))
        story.append(Spacer(1, 3 * mm))

        # ---------------------------------------------------------
        # COMPACT FOOTER
        # ---------------------------------------------------------
        footer = Table(
            [[Paragraph("Computer-generated parcel receipt. If undelivered, return to DailyDrops Fulfillment Center.",
                        center_style)]],
            colWidths=[190 * mm],
        )
        footer.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ]
            )
        )

        story.append(footer)

        document.build(story)
        buffer.seek(0)
        return buffer