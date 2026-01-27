"""
Gerador de PDF - Contrato de Venda
Capital Banq - Documento de 10 páginas
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, Frame, PageTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os


class ContratoVendaPDFGenerator:
    """Gera PDF do Contrato de Venda (10 páginas)"""

    def __init__(self, cliente, beneficio, representante=None, empresa=None):
        self.cliente = cliente
        self.beneficio = beneficio
        self.representante = representante
        self.empresa = empresa
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()

        # Cores do tema (azul/teal como Capital Banq)
        self.cor_azul = colors.HexColor('#2E7D8A')  # Teal/azul para headers
        self.cor_azul_escuro = colors.HexColor('#1A5F6A')
        self.cor_header = colors.HexColor('#1a1a1a')
        self.cor_cinza_claro = colors.HexColor('#F5F5F5')
        self.cor_cinza = colors.HexColor('#CCCCCC')
        self.cor_vermelho = colors.HexColor('#D32F2F')

        # Data atual
        self.data_atual = datetime.now()
        self.data_formatada = self.data_atual.strftime("%d/%m/%Y %H:%M:%S")

        # Número do contrato (ANO + ID do benefício com padding)
        ano = self.data_atual.year
        self.numero_contrato = f"{ano}{str(beneficio.id).zfill(5)}"

        # Calcular taxa de serviço (valor entrada - valor 1ª parcela)
        valor_entrada = float(beneficio.valor_credito or 0) * 0.05  # 5% entrada típica
        self.valor_primeira_parcela = float(beneficio.parcela or 0)
        self.taxa_servico = valor_entrada - self.valor_primeira_parcela if valor_entrada > self.valor_primeira_parcela else 0

        # Local
        self.local = f"{cliente.cidade or 'SÃO PAULO'} - {cliente.estado or 'SP'}"

        self._setup_styles()

    def _setup_styles(self):
        """Configura estilos customizados"""
        # Título do contrato
        self.styles.add(ParagraphStyle(
            name='ContractTitle',
            fontSize=11,
            alignment=TA_CENTER,
            textColor=self.cor_header,
            fontName='Helvetica-Bold',
            leading=14
        ))

        # Texto padrão justificado
        self.styles.add(ParagraphStyle(
            name='ContractText',
            fontSize=9,
            alignment=TA_JUSTIFY,
            textColor=self.cor_header,
            fontName='Helvetica',
            leading=12,
            spaceBefore=3,
            spaceAfter=3
        ))

        # Seção header
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontSize=9,
            alignment=TA_LEFT,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            leftIndent=5
        ))

        # Cláusula título
        self.styles.add(ParagraphStyle(
            name='ClauseTitle',
            fontSize=9,
            alignment=TA_LEFT,
            textColor=self.cor_header,
            fontName='Helvetica-Bold',
            spaceBefore=8,
            spaceAfter=4
        ))

        # Texto pequeno
        self.styles.add(ParagraphStyle(
            name='SmallText',
            fontSize=8,
            alignment=TA_JUSTIFY,
            textColor=self.cor_header,
            fontName='Helvetica',
            leading=10
        ))

        # Texto centralizado
        self.styles.add(ParagraphStyle(
            name='CenterText',
            fontSize=9,
            alignment=TA_CENTER,
            textColor=self.cor_header,
            fontName='Helvetica'
        ))

        # Aviso vermelho
        self.styles.add(ParagraphStyle(
            name='WarningText',
            fontSize=10,
            alignment=TA_CENTER,
            textColor=self.cor_vermelho,
            fontName='Helvetica-Bold'
        ))

    def _format_cpf(self, cpf):
        if not cpf:
            return ''
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf

    def _format_date(self, date):
        if not date:
            return ''
        if isinstance(date, str):
            return date
        return date.strftime("%d/%m/%Y")

    def _format_currency(self, value):
        if not value:
            return 'R$ 0,00'
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def _format_percent(self, value):
        if not value:
            return '0.0 %'
        return f"{float(value):.1f} %"

    def _get_sexo(self):
        sexo = self.cliente.sexo
        if sexo == 'masculino':
            return 'MASCULINO'
        elif sexo == 'feminino':
            return 'FEMININO'
        return sexo.upper() if sexo else ''

    def _get_tipo_bem(self):
        tipo = self.beneficio.tipo_bem
        tipos = {'imovel': 'IMOVEL', 'carro': 'AUTOMOVEL', 'moto': 'MOTOCICLETA'}
        return tipos.get(tipo, tipo.upper() if tipo else '')

    def _create_section_header(self, text, width):
        """Cria cabeçalho de seção com fundo azul/teal"""
        header_table = Table([[Paragraph(text, self.styles['SectionTitle'])]], colWidths=[width])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_azul),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return header_table

    def _create_field_table(self, data, col_widths):
        """Cria tabela de campos com estilo padrão"""
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        return table

    def _create_signature_line(self, label, width=8*cm):
        """Cria linha de assinatura"""
        data = [
            [label],
            ['']
        ]
        table = Table(data, colWidths=[width])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, self.cor_header),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table

    def _add_footer(self, canvas, doc):
        """Adiciona rodapé em cada página"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(1.5*cm, 1*cm, f"Emitido em: {self.data_formatada}")
        canvas.drawRightString(self.width - 1.5*cm, 1*cm, f"Página {doc.page} de 10")
        canvas.restoreState()

    def _page_1(self, elements):
        """Página 1 - Contrato Principal + Dados do Cliente"""
        page_width = self.width - 3*cm

        # Título do contrato
        titulo = """CONTRATO DE CONSULTORIA E SERVIÇOS DIGITAIS PARA
ADESÃO A GRUPO DE CONSÓRCIO DE BENS MÓVEIS E
IMÓVEIS,<b>NÃO CONTEMPLADOS</b>"""
        elements.append(Paragraph(titulo, self.styles['ContractTitle']))

        # Linha separadora
        line = Table([['']], colWidths=[page_width])
        line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1, self.cor_cinza)]))
        elements.append(line)
        elements.append(Spacer(1, 0.3*cm))

        # Texto introdutório em box
        intro = """Por este instrumento particular de CONTRATO, de um lado, a empresa CAPITAL BANQ SOLUÇÕES FINANCEIRAS, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº 60.093.496/0001-17, com sede na Avenida Paulista, 1636, Conj 1504 - Bela Vista, São Paulo - SP, CEP 01310-20, e-mail atendimento@capitalbanq.com.br, neste ato representado por seu representante legal, doravante denominado simplesmente "CONTRATADA", e, de outro lado, o(a) cliente abaixo identificado(a), doravante denominado(a) simplesmente "CONTRATANTE", têm entre si justos e contratados o que segue, nos termos e condições abaixo:"""
        intro_table = Table([[Paragraph(intro, self.styles['SmallText'])]], colWidths=[page_width])
        intro_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(intro_table)
        elements.append(Spacer(1, 0.4*cm))

        # ===== DADOS CADASTRAIS (tabela unificada) =====
        # Header com número do contrato
        header_row = [
            Paragraph("DADOS CADASTRAIS (OBRIGATÓRIO PREENCHER TODOS OS CAMPOS) - CONTRATANTE", self.styles['SectionTitle']),
            Paragraph(f"Nº Contrato: {self.numero_contrato}", ParagraphStyle('Right', fontSize=9, alignment=TA_RIGHT, textColor=colors.white, fontName='Helvetica-Bold'))
        ]

        # Dados do cliente - Tabela unificada
        dados_cadastrais = [
            # Row 1: Labels
            ['Nome/Razão Social do cliente', '', 'Data Nascimento:', 'Sexo:', 'CPF/CNPJ:'],
            # Row 2: Values
            [self.cliente.nome or '', '', self._format_date(self.cliente.data_nascimento), self._get_sexo(), self._format_cpf(self.cliente.cpf)],
            # Row 3: Labels
            ['RG / IE:', 'Data Expedição:', 'Órgão Exp./UF:', 'Profissão:', 'Nacionalidade:'],
            # Row 4: Values
            [self.cliente.identidade or '', self._format_date(self.cliente.data_expedicao), self.cliente.orgao_expedidor or '', self.cliente.cargo or '', self.cliente.nacionalidade or 'BRASILEIRA'],
            # Row 5: Labels
            ['Nome do cônjuge:', '', 'Data Nasc. cônjuge:', '', 'Naturalidade:'],
            # Row 6: Values
            [self.cliente.conjuge_nome or '', '', self._format_date(self.cliente.conjuge_data_nascimento), '', self.cliente.naturalidade or '']
        ]

        col_widths = [4.5*cm, 3*cm, 3.5*cm, 3*cm, 3.5*cm]

        # Header table
        header_table = Table([header_row], colWidths=[page_width * 0.7, page_width * 0.3])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_azul),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
        ]))
        elements.append(header_table)

        # Data table
        dados_table = Table(dados_cadastrais, colWidths=col_widths)
        dados_table.setStyle(TableStyle([
            # Labels rows background
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_cinza_claro),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_cinza_claro),
            # Labels bold
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            # Font size
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            # Span cells
            ('SPAN', (0, 0), (1, 0)),  # Nome label
            ('SPAN', (0, 1), (1, 1)),  # Nome value
            ('SPAN', (0, 4), (1, 4)),  # Cônjuge label
            ('SPAN', (0, 5), (1, 5)),  # Cônjuge value
            ('SPAN', (2, 4), (3, 4)),  # Data nasc cônjuge label
            ('SPAN', (2, 5), (3, 5)),  # Data nasc cônjuge value
        ]))
        elements.append(dados_table)
        elements.append(Spacer(1, 0.4*cm))

        # ===== ENDEREÇO (tabela unificada) =====
        elements.append(self._create_section_header("ENDEREÇO RESIDENCIAL / COMERCIAL", page_width))

        endereco_data = [
            ['Rua/Avenida:', '', '', 'N°:'],
            [f"{self.cliente.logradouro or ''}, {self.cliente.cep or ''}", '', '', self.cliente.numero or ''],
            ['Bairro:', 'Cidade:', '', 'Estado:'],
            [self.cliente.bairro or '', self.cliente.cidade or '', '', self.cliente.estado or ''],
            ['Telefone:', 'Telefone 2:', '', 'E-MAIL:'],
            [self.cliente.telefone or '', self.cliente.telefone_secundario or '', '', self.cliente.email or '']
        ]

        end_col_widths = [5*cm, 5*cm, 2.5*cm, 5*cm]
        endereco_table = Table(endereco_data, colWidths=end_col_widths)
        endereco_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_cinza_claro),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            # Spans
            ('SPAN', (0, 0), (2, 0)),  # Rua label
            ('SPAN', (0, 1), (2, 1)),  # Rua value
            ('SPAN', (1, 2), (2, 2)),  # Cidade label
            ('SPAN', (1, 3), (2, 3)),  # Cidade value
            ('SPAN', (2, 4), (2, 4)),  # Empty
            ('SPAN', (2, 5), (2, 5)),  # Empty
        ]))
        elements.append(endereco_table)
        elements.append(Spacer(1, 0.4*cm))

        # ===== REPRESENTANTE =====
        elements.append(self._create_section_header("REPRESENTANTE AUTORIZADO", page_width))

        empresa_nome = ''
        if self.empresa:
            empresa_nome = self.empresa.nome_fantasia or self.empresa.razao_social or ''
        rep_nome = self.representante.nome if self.representante else ''

        rep_data = [
            ['Empresa:', '', 'Preposto:'],
            [empresa_nome, '', rep_nome],
            ['Assinatura:', '', ''],
        ]

        rep_table = Table(rep_data, colWidths=[8.75*cm, 0.5*cm, 8.25*cm])
        rep_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.cor_cinza_claro),
            ('BACKGROUND', (2, 0), (2, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (0, 2), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('SPAN', (1, 2), (2, 2)),  # Assinatura span
            ('LINEBELOW', (1, 2), (2, 2), 0.5, self.cor_header),
        ]))
        elements.append(rep_table)
        elements.append(Spacer(1, 0.4*cm))

        # ===== TAXAS E VALORES =====
        elements.append(self._create_section_header("TAXAS E VALORES APROXIMADOS DO PLANO A SER CONTRATADO NA ADMINISTRADORA DE CONSÓRCIO", page_width))

        taxas_data = [
            ['Prazo Grupo:', 'Prazo Cota:', 'Valor do Crédito:', 'Valor 1º Parcela:', 'Índice de Correção:'],
            [str(self.beneficio.prazo_grupo or ''), str(self.beneficio.prazo_grupo or ''), self._format_currency(self.beneficio.valor_credito), self._format_currency(self.beneficio.parcela), self.beneficio.indice_correcao or 'INCC'],
            ['Fundo de Reserva:', 'Seguro Prestamista:', 'Tx. Adm. Total:', 'Valor Demais Parcelas:', 'Tipo do Bem:'],
            [self._format_percent(self.beneficio.fundo_reserva), self._format_percent(self.beneficio.seguro_prestamista), self._format_percent(self.beneficio.taxa_administracao), self._format_currency(self.beneficio.valor_demais_parcelas or self.beneficio.parcela), self._get_tipo_bem()],
            ['Grupo:', 'Cota:', 'Qtde. Participantes:', 'Tipo Plano:', ''],
            [self.beneficio.grupo or '', self.beneficio.cota or '', str(self.beneficio.qtd_participantes or ''), self.beneficio.tipo_plano or 'NORMAL', '']
        ]

        taxas_col_widths = [3.5*cm, 3.5*cm, 3.5*cm, 4*cm, 3*cm]
        taxas_table = Table(taxas_data, colWidths=taxas_col_widths)
        taxas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_cinza_claro),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('SPAN', (3, 4), (4, 4)),  # Tipo Plano label
            ('SPAN', (3, 5), (4, 5)),  # Tipo Plano value
        ]))
        elements.append(taxas_table)
        elements.append(Spacer(1, 0.4*cm))

        # ===== RECIBO =====
        elements.append(self._create_section_header("RECIBO E FORMA DO PAGAMENTO INICIAL", page_width))

        recibo1 = f"""Recebemos a importância de {self._format_currency(self.taxa_servico)} na forma abaixo descrita, sendo este valor referente ao pagamento da taxa de serviço da Capital Banq e prestação de serviços de consultoria, aos quais declara o(a) CONTRATANTE ciente de que não se trata de Cota contemplada, Financiamento ou Empréstimo."""

        recibo1_data = [
            [Paragraph(recibo1, self.styles['SmallText'])],
            ['Assinatura do(a) contrante'],
            ['']
        ]
        recibo1_table = Table(recibo1_data, colWidths=[page_width])
        recibo1_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, self.cor_header),
        ]))
        elements.append(recibo1_table)
        elements.append(Spacer(1, 0.2*cm))

        recibo2 = f"""Recebemos a importância de {self._format_currency(self.beneficio.parcela)}, referente a parcela inicial do plano escolhido pela CONTRATANTE. A CONTRATADA a promover a contratação da cota adequada na administradora de consórcio, efetuar a sua adesão sem reservas e transferir os valores correspondentes a parcela inicial do plano aderido, no valor de {self._format_currency(self.beneficio.valor_credito)}."""

        recibo2_data = [
            [Paragraph(recibo2, self.styles['SmallText'])],
            ['Assinatura do(a) contrante'],
            ['']
        ]
        recibo2_table = Table(recibo2_data, colWidths=[page_width])
        recibo2_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, self.cor_header),
        ]))
        elements.append(recibo2_table)

        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(self.local.upper(), self.styles['CenterText']))

        elements.append(PageBreak())

    def _page_2(self, elements):
        """Página 2 - Definições e Obrigações"""
        page_width = self.width - 3*cm

        # CONTA BANCÁRIA
        elements.append(self._create_section_header("CONTA BANCÁRIA INDICADA PELO CLIENTE PARA EVENTUAL CONTEMPLAÇÃO/RESTITUIÇÃO DE VALORES", page_width))

        row_banco = [
            ['Banco:', 'Tipo de Conta:', 'Agência:', 'Conta'],
            [self.cliente.banco or '', self.cliente.tipo_conta or '', self.cliente.agencia or '', self.cliente.conta or ''],
            ['Chave Pix Nominal:', '', '', ''],
            [self.cliente.chave_pix or '', '', '', '']
        ]
        banco_table = Table(row_banco, colWidths=[4.375*cm, 4.375*cm, 4.375*cm, 4.375*cm])
        banco_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (0, 2), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('SPAN', (0, 2), (0, 3)),
            ('SPAN', (1, 2), (-1, 3)),
        ]))
        elements.append(banco_table)

        elements.append(Spacer(1, 0.5*cm))

        # CLÁUSULAS
        # 1. DEFINIÇÃO TERMOS TÉCNICOS
        elements.append(Paragraph("<b>1. DEFINIÇÃO TERMOS TÉCNICOS</b>", self.styles['ClauseTitle']))

        definicoes = [
            "(i) CONSÓRCIO: reunião de pessoas naturais e jurídicas em grupo, com prazo de duração e número de cotas previamente determinados, promovida por administradora de consórcio, com a finalidade de propiciar a seus integrantes, de forma isonômica, a aquisição de bens ou serviços, por meio de autofinanciamento, conforme art. 2º da Lei 11.795/08;",
            "(ii) GRUPO DE CONSÓRCIO: sociedade não personificada constituída por consorciados para os fins estabelecidos no art. 2º da Lei 11.795/2008;",
            "(iii) ADMINISTRADORA DE CONSÓRCIO: pessoa jurídica prestadora de serviços com objeto social principal voltado à administração de grupos de consórcio, constituída sob a forma de sociedade limitada ou sociedade anônima, nos termos do art. 7º, inciso I da Lei 11.795/2008;",
            "(iv) INTERMEDIADORA/MANDATÁRIA: pessoa jurídica prestadora dos serviços de intermediação e assessoramento como a CONTRATADA, visando avaliação específica de seu perfil e necessidade para inclusão em um grupo adequado em administradora de consórcios, devidamente autorizada pelo Banco Central do Brasil (BACEN), com acompanhamento até a contemplação e aquisição do bem ou serviço pretendido. O objeto da INTERMEDIADORA/MANDATÁRIA se constitui de obrigação de meio e não de resultado."
        ]
        for d in definicoes:
            elements.append(Paragraph(d, self.styles['SmallText']))

        # 2. OBJETO
        elements.append(Paragraph("<b>2. OBJETO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("2.1.O presente CONTRATO tem por objeto a prestação de serviços de intermediação especializados, pela CONTRATADA, na prospecção/negociação entre o CONTRATANTE e as administradoras de grupos de consórcio, visando o levantamento de perfil, necessidade e adesão a grupo de consorcio, fornecendo, ainda, suporte até a efetivação de sua contemplação e entrega do bem.", self.styles['SmallText']))
        elements.append(Paragraph("2.1.1. A atuação da CONTRATADA, fica restrita a mediação e/ou intermediação da relação jurídica entre o CONTRATANTE e a administradora do grupo de consórcio, não se responsabilizando ou se solidarizando sobre o referido negócio. Todas as parcelas e taxas devidas à Administradora de Consórcio são responsabilidade da CONTRATANTE.", self.styles['SmallText']))

        # 3. MANDATO
        elements.append(Paragraph("<b>3. MANDATO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("3.1.O(A) CONTRATANTE, para fins de execução deste CONTRATO, confere poderes a empresa CONTRATADA (Capital Banq), para escolha de uma administradora de consórcios, devidamente autorizada pelo poder público, que melhor atenda a seus objetivos. Outorga amplos poderes de representação perante quaisquer administradoras de consórcios, podendo fazer cotações e levantamentos, assinar propostas, contratos, adendos, aditivos, enviar documentos, fazer pesquisas cadastrais, prestar declarações e informações para administradoras com as quais negociar em seu nome, transigir, celebrar contratos, oferecer lances, comparecer em assembleias e nelas votar.", self.styles['SmallText']))
        elements.append(Paragraph("3.2.O(A) CONTRATANTE autoriza ao Capital Banq, às administradoras de consórcios parceiras, de forma direta ou através de seus prestadores de serviços, a formar banco de dados com suas informações para a execução deste contrato, consultar SRC do Banco Central do Brasil, SPC, Serasa e similares.", self.styles['SmallText']))

        # 4. OBRIGAÇÕES DA CONTRATADA
        elements.append(Paragraph("<b>4. OBRIGAÇÕES DA CONTRATADA</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("4.1.Aproximar o(a) CONTRATANTE de uma Administradora de consórcio, indicar e alocá-lo(a) em um grupo de consórcio que melhor atenda o seu perfil, no prazo de 30 (trinta) dias a contar da data da assinatura do presente CONTRATO.", self.styles['SmallText']))
        elements.append(Paragraph("4.1.1. a administradora escolhida, obrigatoriamente, deverá ser autorizada pelo Banco Central do Brasil (BACEN).", self.styles['SmallText']))
        elements.append(Paragraph("4.2.Prestar o atendimento inicial e no transcorrer do grupo, fornecendo suporte ao(a) CONTRATANTE, até a efetivação de sua contemplação e a entrega do bem.", self.styles['SmallText']))
        elements.append(Paragraph("4.2.1. O atendimento será prestado, exclusivamente, por meio telefônico, e-mail e WhatsApp.", self.styles['SmallText']))
        elements.append(Paragraph("4.2.2. quando da contemplação da cota, auxiliar no faturamento do bem ou serviço junto à administradora.", self.styles['SmallText']))

        elements.append(PageBreak())

    def _page_3(self, elements):
        """Página 3 - Obrigações e Condições"""
        # 5. OBRIGAÇÕES DA CONTRATANTE
        elements.append(Paragraph("<b>5. OBRIGAÇÕES DA CONTRATANTE</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("5.1.Fazer cumprir o negócio jurídico aqui celebrado, com a plena ciência das cláusulas deste CONTRATO e demais anexos que os acompanham, devidamente assinados.", self.styles['SmallText']))
        elements.append(Paragraph("5.2.Se portar de acordo com a boa-fé, com integridade e confiabilidade para não frustrar a execução deste contrato. Qualquer prejuízo por informações falsas ou inexatas por parte da CONTRATANTE será de sua exclusiva responsabilidade. Caso a CONTRATADA sofra prejuízos por informações falsas ou inexatas por parte da CONTRATANTE, esta deverá se responsabilizar.", self.styles['SmallText']))
        elements.append(Paragraph("5.3.Manter sempre atualizado o seu endereço, telefone/WhatsApp e PIX, junto à CONTRATADA, informando, por escrito, todas as eventuais alterações, sob pena de perda de prazos e frustração da execução deste contrato, os quais sob nenhuma hipótese será responsabilidade da CONTRATADA.", self.styles['SmallText']))
        elements.append(Paragraph("5.4.Após o seu ingresso ao grupo de consórcio, se obriga a respeitar todas as cláusulas do CONTRATO de adesão e normativos vigentes, bem como contatar a CONTRATADA, sempre que houver dúvida ou esclarecimentos quanto ao negócio pactuado, bem como ao funcionamento do consórcio.", self.styles['SmallText']))
        elements.append(Paragraph("5.5. Efetuar o pagamento das parcelas contratadas com absoluta pontualidade.", self.styles['SmallText']))
        elements.append(Paragraph("5.6. Efetuar a assinatura de documentos da contratação, ofertas de lance, faturamento, de acordo com os prazos consignados.", self.styles['SmallText']))
        elements.append(Paragraph("5.7.O(A) CONTRATANTE declara ter condições econômico-financeiras para assumir as obrigações pretendidas por este contrato, perante o grupo de consórcio, na forma da Resolução BCB nº 285 e 362.", self.styles['SmallText']))

        # 6. SERVIÇOS
        elements.append(Paragraph("<b>6. SERVIÇOS</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("6.1.A CONTRATADA atuará de acordo com as especificações descritas neste instrumento, com ética e responsabilidade. A CONTRATADA, como mandatária da CONTRATANTE, deverá prestar informações acerca das pesquisas, negociações, aprovações de cadastros, cláusulas de contratos, condicionantes de cada proposta, contemplação e faturamento de bens.", self.styles['SmallText']))
        elements.append(Paragraph("6.2.O serviço prestado corresponde à intermediação e/ou mediação entre o(a) CONTRATANTE e a administradora do grupo de consórcio quanto à aquisição de cota de participação, sem que a CONTRATADA realize qualquer ato de administração de cotas de consórcio.", self.styles['SmallText']))
        elements.append(Paragraph("6.2.1.O presente instrumento não se confunde com contrato de adesão a grupo de consórcio, nem com financiamento ou qualquer outra contratação protegida pelo sistema financeiro, tendo caráter exclusivamente de intermediação e assessoria para a adesão em grupo de consórcio e prestação dos serviços de orientação, até a contemplação da cota e entrega do bem.", self.styles['SmallText']))
        elements.append(Paragraph("6.3.Não constitui obrigação da CONTRATADA a realização da venda de cota de participação em grupo de consócios para terceiros.", self.styles['SmallText']))

        # 7. PAGAMENTO
        elements.append(Paragraph("<b>7. PAGAMENTO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("7.1 O pagamento referente ao item RECIBO se refere à serviços de consultoria da CONTRATADA, que deverá ser efetuado somente através de boleto bancário, pix ou depósitos feitos diretamente para o Capital Banq. Jamais poderão ser efetuados pagamentos para colaboradores ou supostos cobradores que não seja o próprio Capital Banq. O valor referente à parcela do consórcio será repassado à Administradora após a sua aprovação", self.styles['SmallText']))

        # 8. PRAZO DO CONTRATO
        elements.append(Paragraph("<b>8. PRAZO DO CONTRATO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("8.1.Os direitos e obrigações iniciam a partir do pagamento total a título de taxa de serviço da Capital Banq e vigerá até a data da contemplação e faturamento do bem ou serviços.", self.styles['SmallText']))
        elements.append(Paragraph("8.1.1.Na hipótese de desistência, pelo(a) CONTRATANTE, após a participação em assembleia ordinária de distribuição de bens, no grupo de consórcio e antes de sua contemplação, o presente instrumento vigerá até a contemplação da cota desistente, sendo obrigação da CONTRATADA, acompanhar e conferir o cálculo dos valores a serem restituídos ao(a) CONTRATANTE.", self.styles['SmallText']))

        # 9. RESCISÃO E DEVOLUÇÃO
        elements.append(Paragraph("<b>9. RESCISÃO E DEVOLUÇÃO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("9.1.O presente CONTRATO é celebrado por prazo determinado, contemplação da cota e entrega do bem ou em caso de desistência do consórcio, a contemplação da cota por desistência, podendo, com antecedência de 30 (trinta) dias, ser denunciado unilateralmente. A denúncia deverá ser encaminhada por escrito e com protocolo de recebimento.", self.styles['SmallText']))

        elements.append(PageBreak())

    def _page_4(self, elements):
        """Página 4 - Disposições Gerais"""
        # Continuação 9. RESCISÃO
        elements.append(Paragraph("9.1.1.Ocorrendo a rescisão pelo CONTRATANTE, este declara ciente que não terá direito à restituição ao valor pago a título de assessoria, visto que, além dos serviços prestados até a data da rescisão, a CONTRATADA permanecerá na obrigação do acompanhamento da cota até a contemplação do(a) CONTRATANTE, junto à administradora de consórcio.", self.styles['SmallText']))
        elements.append(Paragraph("9.1.2.Caso o(a) CONTRATANTE rescinda ou desista da participação no grupo de consórcio, independente do motivo, este declara ciente que terá direito à restituição apenas dos valores comprovadamente transferidos e já pagos à administradora do grupo de consórcio e somente receberá quando da contemplação da cota desistente, nos termos dos artigos 22 e 30, da Lei Federal 11.795/08.", self.styles['SmallText']))
        elements.append(Paragraph("9.1.3.Caso a parte denunciante seja a CONTRATADA, a resilição contratual representará a devolução integral do valor pago a título da assessoria, devidamente corrigido pelo INPC, decotado os valores, comprovadamente, transferidos a administradora de consórcio, permanecendo o(a) CONTRATANTE com as obrigações decorrentes de sua participação no grupo de consórcio.", self.styles['SmallText']))
        elements.append(Paragraph("9.2. O(A) CONTRATANTE poderá rescindir unilateralmente o presente instrumento, por meio de carta escrita de próprio punho, sem necessidade de justificativa, no prazo de até 7 (sete) dias, em conformidade com a Lei Federal nº 8.078/90 (Código de Defesa do Consumidor), com direito à restituição integral do valor de adesão pago, desde que respeitado o disposto na cláusula 9.3.", self.styles['SmallText']))
        elements.append(Paragraph("9.3. Caso a rescisão ocorra após 24 (vinte e quatro) horas da assinatura deste contrato, será aplicada uma multa rescisória de até 20% (vinte por cento) do valor pago, a título de custos operacionais e administrativos, descontada dos valores a serem restituídos ao (à) CONTRATANTE.", self.styles['SmallText']))
        elements.append(Paragraph("9.4. Em caso de cancelamento realizado dentro do prazo legal de 7 (sete) dias corridos, o valor pago pelo(à) CONTRATANTE será restituído no prazo máximo de até 30 (trinta) dias úteis, contados a partir da data da solicitação formal de cancelamento, descontando-se 20% (vinte por cento) do montante total, a título de taxa administrativa da intermediadora, destinada a cobrir os custos operacionais e de intermediação já realizados.", self.styles['SmallText']))

        # 10. INDEPENDÊNCIA
        elements.append(Paragraph("<b>10. INDEPENDÊNCIA ENTRE AS CLÁUSULAS</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("10.1.A não validade, no todo ou em parte, de qualquer disposição deste instrumento, não afetará a validade ou a responsabilidade de quaisquer das outras cláusulas.", self.styles['SmallText']))

        # 11. CONFIDENCIALIDADE
        elements.append(Paragraph("<b>11. CONFIDENCIALIDADE - CLÁUSULA PENAL</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("11.1.As partes se obrigam em manter a confidencialidade de toda a relação negocial deste instrumento e convencionam a título de cláusula penal o pagamento, a quem der causa, de multa pecuniária correspondente ao valor de 10 (dez) vezes ao pagamento total inicial (item 3), devidamente atualizado pelo INCC, à época do descumprimento.", self.styles['SmallText']))

        # 12. DISPOSIÇÕES GERAIS
        elements.append(Paragraph("<b>12. DISPOSIÇÕES GERAIS</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("12.1.Este CONTRATO e as cláusulas que o compõem não poderão se emendados, cancelados, abandonados ou alterados em qualquer forma, exceto através de acordo mútuo, firmado pelas partes.", self.styles['SmallText']))
        elements.append(Paragraph("12.1.Este CONTRATO, uma vez firmado pelas partes, constituirá compromisso irretratável, irrevogável, incondicional e o acordo completo e final entre as partes, substituindo todos os pré-entendimentos, compromissos, cartas, mensagens enviadas pelo aplicativo WhatsApp, e-mails ou correspondências anteriores e em relação à negociação, que mediante este contrato foi firmado e aperfeiçoado.", self.styles['SmallText']))
        elements.append(Paragraph("12.2.Cada cláusula, parágrafo, frase ou sentença deste CONTRATO constitui um compromisso ou disposição independente e distinta. Sempre que possível, cada cláusula deste CONTRATO deverá ser interpretada de modo a se tornar válida e eficaz à luz da lei aplicável. Caso alguma das cláusulas deste CONTRATO seja considerada ilícita, dita cláusula deverá ser julgada separadamente do restante do CONTRATO, e substituída por cláusula lícita e similar, que reflita as intenções originais das partes, observando-se os limites da lei. Todas as demais cláusulas continuarão em pleno vigor.", self.styles['SmallText']))
        elements.append(Paragraph("12.3.Nenhuma disposição deste CONTRATO, seja ela expressa ou tácita, tem a intenção ou deve ser interpretada de modo a conferir a terceiros, direta ou indiretamente, qualquer direito, ou direito a recurso ou demanda judicial referente a este instrumento contratual.", self.styles['SmallText']))
        elements.append(Paragraph("12.4.A tolerância, por qualquer das partes, com relação ao descumprimento de qualquer termo ou condição aqui ajustado, não será considerada como desistência em exigir o cumprimento de disposição nele contida, nem representará novação com relação à obrigação passada, presente ou futura, no tocante ao termo ou condição cujo descumprimento foi tolerado.", self.styles['SmallText']))
        elements.append(Paragraph("12.5.Sobrevindo a ocorrência de casos fortuitos ou força maior que impossibilitem a execução dos serviços e que independam da vontade da CONTRATADA, o CONTRATO poderá ser suspenso até que cesse o referido motivo ou encerrado em comum acordo.", self.styles['SmallText']))
        elements.append(Paragraph("12.6.É defeso a qualquer das partes ceder ou transferir total ou parcial direitos e obrigações decorrentes deste CONTRATO, sem autorização expressa e por escrito de ambas as partes.", self.styles['SmallText']))
        elements.append(Paragraph("12.7.O(A) CONTRATANTE reconhece a inexistência e a exclusão de qualquer espécie de responsabilidade por parte da CONTRATADA, referente a todo e qualquer prejuízo, perda, passivo, custo, demanda, que estejam relacionados ao CONTRATO de participação em grupo de consórcios, junto a administradora de consórcios, escolhida e ratificada pelo(a) CONTRATANTE. As partes se obrigam a observar e cumprir às cláusulas do presente CONTRATO, por si, seus herdeiros e/ou sucessores.", self.styles['SmallText']))
        elements.append(Paragraph("12.8.O(A) CONTRATANTE autoriza expressamente a coleta, tratamento e manutenção de seus dados pela CONTRATADA para a execução deste contrato.", self.styles['SmallText']))

        elements.append(PageBreak())

    def _page_5(self, elements):
        """Página 5 - Declarações e PEP"""
        page_width = self.width - 3*cm

        # 13. DECLARAÇÕES
        elements.append(Paragraph("<b>13. DECLARAÇÕES E DO CONHECIMENTO PRÉVIO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("13.1.O(A) CONTRATANTE, neste ato, declara saber que:", self.styles['SmallText']))
        elements.append(Paragraph("(i) nenhuma promessa ou proposta extracontratual e extra normativos do sistema de consórcios lhe foi feita. Informa que leu atentamente todas as cláusulas e condições do presente instrumento, obtendo assim, todas as informações necessárias para o perfeito conhecimento das regras de funcionamento do produto consórcio e que autoriza sua contabilização definitiva na empresa escolhida, sem nenhuma restrição;", self.styles['SmallText']))
        elements.append(Paragraph("(ii) ALERTA AO CONSUMIDOR: Nenhum documento, promessa escrita, verbal ou gravada, feitas ou firmadas por terceiros, ou mesmo por funcionários sem poderes de gestão, que não sejam os representantes legais da CONTRATADA, não terão nenhuma validade, prevalecendo somente as cláusulas contratuais;", self.styles['SmallText']))
        elements.append(Paragraph("(i)que autoriza a CONTRATADA a consultar quaisquer informações disponibilizadas pelos órgãos de proteção ao crédito.", self.styles['SmallText']))
        elements.append(Paragraph("(ii) Em caso de desistência por parte da CONTRATANTE, os valores pagos a título de intermediação e assessoria não poderão ser devolvidos por se tratar de serviço já prestado.", self.styles['SmallText']))

        # 14. FORO
        elements.append(Paragraph("<b>14. FORO</b>", self.styles['ClauseTitle']))
        elements.append(Paragraph("14.1.Para dirimir quaisquer questões oriundas do presente CONTRATO, as partes elegem o foro da Comarca de São Paulo, Estado de São Paulo, com renúncia expressa de qualquer outro, por mais privilegiado que seja ou venha a ser.", self.styles['SmallText']))

        elements.append(Spacer(1, 0.5*cm))

        # Data e Local
        data_extenso = self._get_data_extenso()
        elements.append(Paragraph(f"SÃO PAULO-SP, {data_extenso}.", self.styles['CenterText']))

        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas
        sig_data = [
            ['Assinatura da CONTRATADA', 'Assinatura do(a) CONTRATANTE'],
            ['', '']
        ]
        sig_table = Table(sig_data, colWidths=[8.75*cm, 8.75*cm])
        sig_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 1), (0, 1), 0.5, self.cor_header),
            ('LINEBELOW', (1, 1), (1, 1), 0.5, self.cor_header),
            ('TOPPADDING', (0, 1), (-1, 1), 20),
        ]))
        elements.append(sig_table)

        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("<b>TESTEMUNHAS</b>", self.styles['CenterText']))

        test_data = [['', ''], ['', '']]
        test_table = Table(test_data, colWidths=[8.75*cm, 8.75*cm])
        test_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 0.5, self.cor_header),
            ('LINEBELOW', (1, 0), (1, 0), 0.5, self.cor_header),
            ('TOPPADDING', (0, 0), (-1, 0), 20),
        ]))
        elements.append(test_table)

        elements.append(Spacer(1, 0.5*cm))

        # DECLARAÇÃO PEP
        elements.append(self._create_section_header("DECLARAÇÃO DE PESSOA POLITICAMENTE EXPOSTA-PEP", page_width))

        pep_intro = """O objetivo desta declaração é atender as diretrizes do Banco Central do Brasil Bacen e do COAF/UIF que administradoras de consórcio devem adotar, para controles e acompanhamento dos negócios e movimentações financeiras das pessoas politicamente expostas a fim de atender dispostos na lei 9.613 de 3 de Março de 1998."""
        elements.append(Paragraph(pep_intro, self.styles['SmallText']))

        pep_def = """São considerados pessoas politicamente expostas Todas aquelas que previstas no artigo 4o da circular do Banco Central do Brasil BACEN de no 3.461 de 24 de julho de 2009 da qual consorciado abaixo-assinado declara ter conhecimento."""
        elements.append(Paragraph(pep_def, self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*cm))

        elements.append(Paragraph("• Sou pessoa politicamente exposta __________.", self.styles['SmallText']))
        elements.append(Paragraph("• Possuo parentes de primeiro grau pais ou filhos cônjuges companheiro, enteado inclusive representante pessoas que possam ter minha a procuração que possam ser considerados pessoas politicamente expostas __________.", self.styles['SmallText']))
        elements.append(Paragraph("• Estou enquadrado como Estreito colaborador de pessoa politicamente exposta como definido pelo coaf __________.", self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*cm))

        pep_decl = """Declaro sob as penas da lei que as informações aqui prestadas são expressão da Verdade pelas quais me responsabilizo com a veracidade e exatidão das informações prestadas."""
        elements.append(Paragraph(pep_decl, self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*cm))

        # Dados do cliente
        cliente_data = [
            ['Nome', 'CPF', 'RG'],
            [self.cliente.nome or '', self._format_cpf(self.cliente.cpf), self.cliente.identidade or '']
        ]
        elements.append(self._create_field_table(cliente_data, [9*cm, 4*cm, 4.5*cm]))

        # Local/Data e Assinatura
        loc_data = [
            ['Local/Data', 'Assinatura do consorciado / Conforme documento'],
            [f"SÃO PAULO-SP, {data_extenso}.", '']
        ]
        loc_table = Table(loc_data, colWidths=[8.75*cm, 8.75*cm])
        loc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('LINEBELOW', (1, 1), (1, 1), 0.5, self.cor_header),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(loc_table)

        elements.append(PageBreak())

    def _page_6(self, elements):
        """Página 6 - Declaração de Ciência"""
        page_width = self.width - 3*cm
        data_extenso = self._get_data_extenso()

        elements.append(Spacer(1, 2*cm))

        # Título
        elements.append(self._create_section_header("DECLARAÇÃO DE CIÊNCIA", page_width))

        elements.append(Spacer(1, 0.5*cm))

        elements.append(Paragraph("Declaro para os devidos fins de Direito que ao contratar os serviços :", self.styles['SmallText']))

        ciencia_text = f"""Tomou ciência na data de hoje, que do valor pago nessa ocasião da contratação será passado o valor aproximado de {self._format_currency(self.beneficio.parcela)} para a administradora de consórcios, a ser contratada a título de primeira parcela do consórcio, e o saldo remanescente será utilizado para pagamentos de custas de contratação da intermediação tais como custas comerciais, e administrativas conforme contrato de intermediação na adesão a grupo de consórcio não contemplados. Desde já fica autorizado tais repasses descritos aqui, através dessa declaração e ratificação através do instrumento particular de contratação, aditivos e checagem telefônica gravada."""
        elements.append(Paragraph(ciencia_text, self.styles['SmallText']))

        elements.append(Spacer(1, 1*cm))

        # Dados do cliente
        cliente_data = [
            ['Nome', 'CPF', 'RG'],
            [self.cliente.nome or '', self._format_cpf(self.cliente.cpf), self.cliente.identidade or '']
        ]
        elements.append(self._create_field_table(cliente_data, [9*cm, 4*cm, 4.5*cm]))

        # Local/Data e Assinatura
        loc_data = [
            ['Local/Data', 'Assinatura do consorciado / Conforme documento'],
            [f"SÃO PAULO-SP, {data_extenso}.", '']
        ]
        loc_table = Table(loc_data, colWidths=[8.75*cm, 8.75*cm])
        loc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('LINEBELOW', (1, 1), (1, 1), 0.5, self.cor_header),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(loc_table)

        elements.append(PageBreak())

    def _page_7(self, elements):
        """Página 7 - Termo de Consultoria (versão 1)"""
        page_width = self.width - 3*cm
        data_extenso = self._get_data_extenso()

        elements.append(Spacer(1, 1*cm))

        # Título
        elements.append(self._create_section_header("TERMO DE CONTRATAÇÃO DE SERVIÇOS DE CONSULTORIA FINANCEIRA", page_width))

        elements.append(Spacer(1, 0.5*cm))

        intro = """A Capital Banq atua exclusivamente na consultoria financeira para aquisição de consórcios não contemplados, facilitando a conexão entre o cliente e a administradora de consórcios. Essa consultoria é realizada por meio de seus consultores credenciados, que são pessoas jurídicas autônomas e possuem liberdade para cobrar pelos serviços de atendimento e vendas prestadas."""
        elements.append(Paragraph(intro, self.styles['SmallText']))

        declaracoes = [
            "O(a) PROPONENTE declara, conforme a lei, que preencheu uma proposta de consultoria financeira com a Capital Banq para adquirir um consórcio não contemplado e está ciente de que deve aguardar a contemplação por meio de sorteio pela Loteria Federal ou lance, conforme o regulamento geral de consórcios.",
            "O(a) PROPONENTE está ciente de que sua proposta será comprovada pelo setor de qualidade da Capital Banq e, somente após validação, seu contrato será apresentado à administradora e incluído no grupo de consórcio.",
            "O(a) PROPONENTE declara ter lido e compreendido todas as cláusulas do regulamento do consórcio, em conformidade com a Lei nº 11.795/2008, incluindo suas obrigações, taxas e formas de contemplação, e que não restam dúvidas sobre a negociação assumida.",
            "O(a) PROPONENTE autoriza que a contratação de uma consultoria financeira para consórcio não é obrigatória, mas aceita livremente os termos e condições contratuais propostas.",
            "O(a) PROPONENTE também declara estar ciente de que os valores pagos na adesão referem-se à inclusão no grupo de consórcio, à taxa administrativa da administradora e à taxa de consultoria pela prestação de serviços da Capital Banq."
        ]

        for d in declaracoes:
            elements.append(Paragraph(d, self.styles['SmallText']))

        elements.append(Spacer(1, 1*cm))

        # Dados do cliente
        cliente_data = [
            ['Nome', 'CPF', 'RG'],
            [self.cliente.nome or '', self._format_cpf(self.cliente.cpf), self.cliente.identidade or '']
        ]
        elements.append(self._create_field_table(cliente_data, [9*cm, 4*cm, 4.5*cm]))

        # Local/Data e Assinatura
        loc_data = [
            ['Local/Data', 'Assinatura do consorciado / Conforme documento'],
            [f"SÃO PAULO-SP, {data_extenso}.", '']
        ]
        loc_table = Table(loc_data, colWidths=[8.75*cm, 8.75*cm])
        loc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.cor_cinza),
            ('LINEBELOW', (1, 1), (1, 1), 0.5, self.cor_header),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(loc_table)

        elements.append(PageBreak())

    def _page_8(self, elements):
        """Página 8 - Termo de Consultoria (versão 2)"""
        page_width = self.width - 3*cm
        data_extenso = self._get_data_extenso()

        elements.append(Spacer(1, 1*cm))

        # Título
        elements.append(self._create_section_header("TERMO DE CONTRATAÇÃO DE SERVIÇOS DE CONSULTORIA FINANCEIRA", page_width))

        elements.append(Spacer(1, 0.5*cm))

        intro = """A Capital Banq atua como consultora financeira, promovendo a assessoria na aquisição de consórcios não contemplados entre o(a) CONTRATANTE e a Administradora de Consórcios, por meio de seus consultores financeiros devidamente credenciados, que possuem independência para realizar a cobrança pelos serviços prestados de atendimento e vendas."""
        elements.append(Paragraph(intro, self.styles['SmallText']))

        declaracoes = [
            "O(a) PROPONENTE declara, sob as penas da lei, que preencheu uma proposta de consultoria financeira junto à Capital Banq com o objetivo de adquirir uma cota de consórcio não contemplada. O(a) PROPONENTE compreende que a contemplação ocorrerá em conformidade com os termos do regulamento geral da Administradora, seja por sorteio automático ou por lance, e se obrigará a efetuar o pagamento das parcelas rigorosamente em dia.",
            "O(a) PROPONENTE está ciente de que uma proposta será comprovada pela Administradora de Consórcios e pela Capital Banq, que poderá recusar o caso não atender às exigências legais e às políticas internas da Administradora.",
            "O(a) PROPONENTE declara estar ciente de que o cancelamento do consórcio após a facilidade da proposta poderá gerar prejuízos financeiros à Capital Banq e aos consultores responsáveis pela intermediação, comprometendo-se a reparar eventuais perdas e danos, incluindo a garantia da comissão de corretagem para o consultor envolvido na revenda da cota.",
            "O(a) PROPONENTE confirma ter lido e compreende todas as cláusulas do regulamento do consórcio, bem como as obrigações e direitos relacionados à contratação, não restando dúvidas sobre a negociação assumida, conforme previsto na Lei nº 11.795/2008.",
            "O(a) PROPONENTE autoriza que a contratação de uma consultoria financeira não é obrigatória para a aquisição de consórcio, mas aceita voluntariamente os termos e condições contratuais ou pactuados.",
            "O(a) PROPONENTE concorda que, dos valores pagos na taxa de adesão, a comissão de corretagem será repassada aos consultores de consórcios, autorizando desde já o pagamento sem que isso gere qualquer prejuízo à Capital Banq."
        ]

        for d in declaracoes:
            elements.append(Paragraph(d, self.styles['SmallText']))

        elements.append(Spacer(1, 0.5*cm))

        # Aviso
        elements.append(Paragraph("LEIA COM ATENÇÃO ANTES DE ASSINAR.", self.styles['WarningText']))

        elements.append(Spacer(1, 0.3*cm))

        elements.append(Paragraph(f"SÃO PAULO-SP, {data_extenso}.", self.styles['CenterText']))

        elements.append(Spacer(1, 0.2*cm))

        elements.append(Paragraph("NÃO COMERCIALIZAMOS COTAS CONTEMPLADAS.", self.styles['WarningText']))

        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas
        rep_nome = self.representante.nome if self.representante else ''
        cliente_cpf = f"{self.cliente.nome or ''} - {self._format_cpf(self.cliente.cpf)}"

        sig_data = [
            ['Nome legível do Vendedor'],
            [rep_nome],
            [''],
            ['Nome do cliente + CPF do cliente'],
            [cliente_cpf],
            ['']
        ]
        sig_table = Table(sig_data, colWidths=[page_width])
        sig_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 1), (0, 1), 0.5, self.cor_header),
            ('LINEBELOW', (0, 4), (0, 4), 0.5, self.cor_header),
            ('TOPPADDING', (0, 1), (0, 1), 5),
            ('TOPPADDING', (0, 4), (0, 4), 5),
        ]))
        elements.append(sig_table)

        elements.append(PageBreak())

    def _page_9(self, elements):
        """Página 9 - Questionário de Checagem"""
        page_width = self.width - 3*cm

        elements.append(Spacer(1, 0.5*cm))

        # Título
        elements.append(self._create_section_header("TERMO DE CONTRATAÇÃO DE SERVIÇOS DE CONSULTORIA FINANCEIRA", page_width))

        elements.append(Spacer(1, 0.3*cm))

        intro = """Parabéns pela aquisição da sua cota de consórcio é um prazer tê-lo como cliente!

Esperamos poder contar com a sua colaboração para que possamos proceder corretamente com o seu cadastro de contrato, e ao mesmo tempo realizar uma avaliação da qualidade do serviço prestado pelo nosso consultor de vendas. Para que isso ocorra pedimos que responda o questionário abaixo com sim ou não:"""
        elements.append(Paragraph(intro, self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*cm))

        # Questionário
        perguntas = [
            "Você contratou um serviço de Consultora com a Capital Banq para participar de um consórcio não contemplado? __________",
            "Você confirma que possuiu capacidade financeira para arcar com as prestações do seu consórcio? __________",
            f"Você está de ciente que o valor da sua parcela mensal é de {self._format_currency(self.beneficio.parcela)} __________",
            "Tomou ciência que a empresa Capital Banq não administra consórcios, apenas promove a consultoria? __________",
            "Você tem ciência que o consórcio não está contemplado? __________",
            "Foi informado(a) de que a contemplação ocorrerá somente por sorteio ou lance fixo ou lance Livre? __________",
            "Lhe foi feita alguma promessa de contemplação, garantia de contemplação em determinado prazo, mediante determinado valor de lance ou vantagens extras? __________",
            "Ocorrendo a rescisão pelo CONTRATANTE, este declara ciente que não terá direito à restituição ao valor pago a título de assessoria, visto que, além dos serviços prestados até a data da rescisão, a CONTRATADA permanecerá na obrigação do acompanhamento da cota até a contemplação do(a) CONTRATANTE, junto a administradora de consórcio. __________",
            "Você leu com atenção todo o contrato de intermediação para adesão a grupo de consórcio e assinou concordando com as cláusulas e condições somente depois da leitura? __________",
            "Você escolheu participar de um consórcio intermediado pela Capital Banq e administrado por Administradoras de Consórcios autorizadas e fiscalizadas pelo Banco Central? __________"
        ]

        for p in perguntas:
            elements.append(Paragraph(p, self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*cm))

        aviso = """Promovemos a intermediação entre o interessado em consórcio e a administradora legalmente autorizadas pelo Banco Central, através de seus corretores pessoa Jurídica autônomos credenciados.

Prezado cliente, os seus dados serão inseridos no sistema da administradora e você receberá no seu e-mail o regulamento do consórcio adquirido. Você receberá também, seu grupo e a cota."""
        elements.append(Paragraph(aviso, self.styles['SmallText']))

        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas
        rep_nome = self.representante.nome if self.representante else ''
        cliente_cpf = f"{self.cliente.nome or ''} - {self._format_cpf(self.cliente.cpf)}"

        sig_data = [
            ['Nome legível do Vendedor'],
            [rep_nome],
            [''],
            ['Nome do cliente + CPF do cliente'],
            [cliente_cpf],
            ['']
        ]
        sig_table = Table(sig_data, colWidths=[page_width])
        sig_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 1), (0, 1), 0.5, self.cor_header),
            ('LINEBELOW', (0, 4), (0, 4), 0.5, self.cor_header),
            ('TOPPADDING', (0, 1), (0, 1), 5),
            ('TOPPADDING', (0, 4), (0, 4), 5),
        ]))
        elements.append(sig_table)

        elements.append(PageBreak())

    def _page_10(self, elements):
        """Página 10 - Ciência da Análise Creditícia"""
        page_width = self.width - 3*cm
        data_extenso = self._get_data_extenso()

        elements.append(Spacer(1, 0.5*cm))

        # Título
        elements.append(self._create_section_header("CIÊNCIA E CONCORDÂNCIA COM A ANÁLISE CREDITÍCIA PRÉVIA À AQUISIÇÃO DE COTA DE CONSÓRCIO", page_width))

        elements.append(Spacer(1, 0.5*cm))

        declaracoes = [
            "1. Estou ciente de que, após realização de uma simulação na data de assinatura deste, com base em consultas aos órgãos de proteção ao crédito, na renda por mim informada e nos documentos por mim apresentados, fui devidamente informado quanto à aprovação ou reprovação do crédito, no cenário ATUAL, se hoje houvesse a contemplação de cota, seja por sorteio, seja por lance;",
            "2. Estou ciente, ainda, de que o cenário ATUAL está sujeito a mudanças, podendo variar diária, semanal ou mensalmente, conforme as minhas condições pessoais também se alterem (profissão, renda, estado civil, restrições etc.);",
            "3. Desta forma, estou ciente e de acordo que o status de aprovação ou reprovação pode sofrer alteração a qualquer tempo conforme minhas condições pessoais também se alterem, sendo que nova análise poderá ser realizada no momento da contemplação;",
            "4. Por fim, declaro que fui informado sobre a análise creditícia e assinei o presente contrato antes de efetivar a minha adesão a qualquer grupo de consórcio. Declaro que foi ofertado respeitando as leis vigentes em observância ao Código de Defesa do Consumidor e Lei 11.795/2008, deixando claro que a decisão de dar continuidade na compra foi minha, ciente dos prazos e regulamentos atuais."
        ]

        for d in declaracoes:
            elements.append(Paragraph(d, self.styles['SmallText']))

        elements.append(Spacer(1, 0.3*cm))

        declaracao_final = """Declaro expressamente de estar ciente que em decorrência da minha incapacidade financeira junto às instituições de crédito, as quais indeferiram a aquisição mediante financiamento do bem, autorizo a contratada a proceder com a aquisição do bem por meio de aquisição de cotas de participação em grupo de consorcio, nos termos elencados no contrato que me foi fornecido e cientificado das cláusulas com a devia antecedência."""
        elements.append(Paragraph(declaracao_final, self.styles['SmallText']))

        elements.append(Spacer(1, 0.5*cm))

        # Aviso
        elements.append(Paragraph("LEIA COM ATENÇÃO ANTES DE ASSINAR.", self.styles['WarningText']))

        elements.append(Spacer(1, 0.5*cm))

        elements.append(Paragraph(f"SÃO PAULO-SP, {data_extenso}.", self.styles['CenterText']))

        elements.append(Spacer(1, 0.2*cm))

        elements.append(Paragraph("NÃO COMERCIALIZAMOS COTAS CONTEMPLADAS.", self.styles['WarningText']))

        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas
        rep_nome = self.representante.nome if self.representante else ''
        cliente_cpf = f"{self.cliente.nome or ''} - {self._format_cpf(self.cliente.cpf)}"

        sig_data = [
            ['Nome legível do Vendedor'],
            [rep_nome],
            [''],
            ['Nome do cliente + CPF do cliente'],
            [cliente_cpf],
            ['']
        ]
        sig_table = Table(sig_data, colWidths=[page_width])
        sig_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 1), (0, 1), 0.5, self.cor_header),
            ('LINEBELOW', (0, 4), (0, 4), 0.5, self.cor_header),
            ('TOPPADDING', (0, 1), (0, 1), 5),
            ('TOPPADDING', (0, 4), (0, 4), 5),
        ]))
        elements.append(sig_table)

    def _get_data_extenso(self):
        """Retorna data por extenso"""
        meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        dia = self.data_atual.day
        mes = meses[self.data_atual.month - 1]
        ano = self.data_atual.year
        return f"{dia} de {mes} de {ano}"

    def generate(self):
        """Gera o PDF completo"""
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1*cm,
            bottomMargin=1.5*cm
        )

        elements = []

        # Gerar todas as páginas
        self._page_1(elements)
        self._page_2(elements)
        self._page_3(elements)
        self._page_4(elements)
        self._page_5(elements)
        self._page_6(elements)
        self._page_7(elements)
        self._page_8(elements)
        self._page_9(elements)
        self._page_10(elements)

        # Build com rodapé
        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        buffer.seek(0)
        return buffer.getvalue()

    def get_filename(self):
        """Retorna nome do arquivo"""
        nome_limpo = (self.cliente.nome or 'cliente').replace(' ', '_')
        return f"contrato_venda_{nome_limpo}_{self.numero_contrato}.pdf"
