# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

from datetime import datetime
from lxml import etree
from StringIO import StringIO
import base64
import logging
import zeep

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'firma_gface': fields.char('Firma GFACE', copy=False),
        'pdf_gface': fields.binary('PDF GFACE', copy=False),
    }

    def invoice_validate(self, cr, uid, ids, context=None):

        detalles = []
        subtotal = 0
        for factura in self.browse(cr, uid, ids, context=context):
            if factura.journal_id.clave_gface and not factura.firma_gface:

                stdTWS = etree.Element("stdTWS", xmlns="GFACE_Web")
                stdTWSCIt = etree.SubElement(stdTWS, "stdTWS.stdTWSCIt")

                TrnLotNum = etree.SubElement(stdTWSCIt, "TrnLotNum")
                TrnLotNum.text = "0"
                TipTrnCod = etree.SubElement(stdTWSCIt, "TipTrnCod")
                TipTrnCod.text = factura.journal_id.tipo_documento_gface
                TrnNum = etree.SubElement(stdTWSCIt, "TrnNum")
                TrnNum.text = str(factura.id)
                TrnFec = etree.SubElement(stdTWSCIt, "TrnFec")
                TrnFec.text = factura.date_invoice
                TrnBenConNIT = etree.SubElement(stdTWSCIt, "TrnBenConNIT")
                TrnBenConNIT.text = factura.partner_id.vat
                TrnEFACECliCod = etree.SubElement(stdTWSCIt, "TrnEFACECliCod")
                TrnEFACECliNom = etree.SubElement(stdTWSCIt, "TrnEFACECliNom")
                TrnEFACECliNom.text = factura.partner_id.name
                TrnEFACECliDir = etree.SubElement(stdTWSCIt, "TrnEFACECliDir")
                TrnEFACECliDir.text = factura.partner_id.street
                TrnObs = etree.SubElement(stdTWSCIt, "TrnObs")
                TrnEMail = etree.SubElement(stdTWSCIt, "TrnEMail")
                if factura.partner_id.email:
                    TrnEMail.text = factura.partner_id.email
                TDFEPAutResNum = etree.SubElement(stdTWSCIt, "TDFEPAutResNum")
                TDFEPTipTrnCod = etree.SubElement(stdTWSCIt, "TDFEPTipTrnCod")
                TDFEPSerie = etree.SubElement(stdTWSCIt, "TDFEPSerie")
                TDFEPDispElec = etree.SubElement(stdTWSCIt, "TDFEPDispElec")
                TDFEPYear = etree.SubElement(stdTWSCIt, "TDFEPYear")
                TDFEPYear.text = "0"
                TDFEPNum = etree.SubElement(stdTWSCIt, "TDFEPNum")
                TDFEPNum.text = "0"
                MonCod = etree.SubElement(stdTWSCIt, "MonCod")
                MonCod.text = "GTQ"
                TrnTasCam = etree.SubElement(stdTWSCIt, "TrnTasCam")
                TrnTasCam.text = "1"
                # TrnCampAd01 = etree.SubElement(stdTWSCIt, "TrnCampAd01")
                TrnPaisCod = etree.SubElement(stdTWSCIt, "TrnPaisCod")
                TrnUltLinD = etree.SubElement(stdTWSCIt, "TrnUltLinD")
                TrnUltLinD.text = str(len(factura.invoice_line))

                stdTWSD = etree.SubElement(stdTWSCIt, "stdTWSD")

                num = 1
                for linea in factura.invoice_line:
                    stdTWSDIt = etree.SubElement(stdTWSD, "stdTWS.stdTWSCIt.stdTWSDIt")

                    TrnLiNum = etree.SubElement(stdTWSDIt, "TrnLiNum")
                    TrnLiNum.text = str(num)
                    num += 1
                    TrnArtCod = etree.SubElement(stdTWSDIt, "TrnArtCod")
                    if linea.product_id.default_code:
                        TrnArtCod.text = linea.product_id.default_code
                    else:
                        TrnArtCod.text = str(linea.product_id.id)
                    TrnArtNom = etree.SubElement(stdTWSDIt, "TrnArtNom")
                    TrnArtNom.text = linea.name
                    TrnCan = etree.SubElement(stdTWSDIt, "TrnCan")
                    TrnCan.text = str(linea.quantity)
                    TrnVUn = etree.SubElement(stdTWSDIt, "TrnVUn")
                    TrnVUn.text = str(linea.price_unit)
                    TrnUniMed = etree.SubElement(stdTWSDIt, "TrnUniMed")
                    TrnUniMed.text = "UNIDAD"
                    TrnVDes = etree.SubElement(stdTWSDIt, "TrnVDes")
                    TrnVDes.text = "0.00"
                    TrnArtBienSer = etree.SubElement(stdTWSDIt, "TrnArtBienSer")
                    if linea.product_id.type == 'product':
                        TrnArtBienSer.text = "0"
                    else:
                        TrnArtBienSer.text = "1"
                    TrnArtExcento = etree.SubElement(stdTWSDIt, "TrnArtExcento")
                    TrnArtExcento.text = "0"
                    TrnDetCampAd01 = etree.SubElement(stdTWSDIt, "TrnDetCampAd01")
                    TrnDetCampAd02 = etree.SubElement(stdTWSDIt, "TrnDetCampAd02")
                    TrnDetCampAd03 = etree.SubElement(stdTWSDIt, "TrnDetCampAd03")
                    TrnDetCampAd04 = etree.SubElement(stdTWSDIt, "TrnDetCampAd04")
                    TrnDetCampAd05 = etree.SubElement(stdTWSDIt, "TrnDetCampAd05")

                stdTWSIA = etree.SubElement(stdTWSCIt, "stdTWSIA")

                xmls = etree.tostring(stdTWS, xml_declaration=True, encoding="UTF-8")
                logging.warn(xmls)

                wsdl = "https://gface.ecofactura.com.gt:8443/gface/servlet/ar_car_fac?wsdl"
                client = zeep.Client(wsdl=wsdl)

                resultado = client.service.Execute(factura.journal_id.nit_emisor_gface, factura.journal_id.clave_gface, factura.journal_id.nit_emisor_gface, factura.journal_id.numero_establecimiento_gface, factura.journal_id.resolucion_gface, xmls, 1)
                # logging.warn(resultado)

                if resultado.Dte:
                    archivos = etree.parse(StringIO(resultado.Dte))
                    dte = archivos.xpath("/DTE/CFDArchivo[@Tipo='XML']")
                    cfd = etree.parse(StringIO(base64.b64decode(dte[0].get("Archivo"))))

                    firma = cfd.xpath("//*[local-name()='SignatureValue']")[0].text
                    numero = cfd.xpath("//dcae")[0].get("id")
                    logging.warn(numero)

                    pdf = archivos.xpath("/DTE/CFDArchivo[@Tipo='PDF']")[0].get("Archivo")

                    self.write(cr, uid, ids, { "firma_gface": firma, 'name': numero, 'pdf_gface': pdf })
                else:
                    raise osv.except_osv('Error', resultado.Respuesta)

        return super(account_invoice,self).invoice_validate(cr, uid, ids, context)

class account_journal(osv.osv):
    _inherit = "account.journal"

    _columns = {
        'nit_emisor_gface': fields.char('NIT Emisor GFACE'),
        'clave_gface': fields.char('Clave GFACE'),
        'numero_establecimiento_gface': fields.char('Numero de Establecimiento GFACE'),
        'resolucion_gface': fields.char('Numero Resolucion GFACE'),
        'tipo_documento_gface': fields.selection((('FACE-63', 'FACE-63'),), 'Tipo de Documento GFACE'),
    }
