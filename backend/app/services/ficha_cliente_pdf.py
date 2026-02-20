"""
Gerador de PDF - Ficha de Atendimento do Cliente
HM Capital - Documento profissional de 3 páginas
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os


class FichaClientePDFGenerator:
    """Gera PDF profissional da Ficha de Atendimento do Cliente"""

    def __init__(self, cliente, representante=None):
        self.cliente = cliente
        self.representante = representante
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()

        # Cores do tema HM Capital (verde e dourado)
        self.cor_verde = colors.HexColor('#1B5E20')
        self.cor_verde_claro = colors.HexColor('#2E7D32')
        self.cor_dourada = colors.HexColor('#C4A962')
        self.cor_dourada_escura = colors.HexColor('#A68B4B')
        self.cor_header = colors.HexColor('#1a1a1a')
        self.cor_cinza_claro = colors.HexColor('#F5F5F5')
        self.cor_cinza = colors.HexColor('#E0E0E0')

        # Caminho do logo
        self.logo_path = os.path.join(
            os.path.dirname(__file__), '..', 'static', 'images', 'logo-hm-capital.png'
        )

        # Data atual
        self.data_atual = datetime.now()
        self.data_formatada = self.data_atual.strftime("%d/%m/%Y")

        self._setup_styles()

    def _setup_styles(self):
        """Configura estilos customizados"""
        # Título da capa
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            fontSize=28,
            alignment=TA_CENTER,
            textColor=self.cor_verde,
            fontName='Helvetica-Bold',
            spaceAfter=10,
            leading=34
        ))

        # Subtítulo da capa
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontSize=16,
            alignment=TA_CENTER,
            textColor=self.cor_dourada_escura,
            fontName='Helvetica-Bold',
            spaceAfter=5
        ))

        # Nome do cliente na capa
        self.styles.add(ParagraphStyle(
            name='ClienteName',
            fontSize=24,
            alignment=TA_CENTER,
            textColor=self.cor_header,
            fontName='Helvetica-Bold',
            spaceAfter=10
        ))

        # Texto motivacional
        self.styles.add(ParagraphStyle(
            name='MotivationalText',
            fontSize=12,
            alignment=TA_CENTER,
            textColor=self.cor_verde,
            fontName='Helvetica-Oblique',
            leading=16
        ))

        # Header de seção (fundo dourado)
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        ))

        # Header principal da página
        self.styles.add(ParagraphStyle(
            name='PageHeader',
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        ))

        # Labels dos campos
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            fontSize=6,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

        # Valores dos campos
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica'
        ))

        # Texto do rodapé
        self.styles.add(ParagraphStyle(
            name='FooterText',
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray,
            fontName='Helvetica'
        ))

        # Texto de proposta
        self.styles.add(ParagraphStyle(
            name='PropostaTitle',
            fontSize=12,
            alignment=TA_LEFT,
            textColor=self.cor_verde,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='PropostaContent',
            fontSize=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica',
            leading=14
        ))

    # ==================== FORMATADORES ====================

    def _format_cpf(self, cpf):
        if not cpf:
            return ""
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf

    def _format_telefone(self, tel):
        if not tel:
            return ""
        tel = ''.join(filter(str.isdigit, str(tel)))
        if len(tel) == 11:
            return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:
            return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        return tel

    def _format_date(self, date):
        if not date:
            return ""
        if isinstance(date, str):
            try:
                from datetime import datetime as dt
                d = dt.fromisoformat(date.replace('Z', '+00:00'))
                return d.strftime("%d/%m/%Y")
            except:
                return date
        return date.strftime("%d/%m/%Y")

    def _format_currency(self, value):
        if not value:
            return ""
        try:
            return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return str(value)

    def _format_cep(self, cep):
        if not cep:
            return ""
        cep = ''.join(filter(str.isdigit, str(cep)))
        if len(cep) == 8:
            return f"{cep[:5]}-{cep[5:]}"
        return cep

    def _get_estado_civil(self):
        mapping = {
            'solteiro': 'Solteiro(a)',
            'casado': 'Casado(a)',
            'divorciado': 'Divorciado(a)',
            'viuvo': 'Viúvo(a)',
            'uniao_estavel': 'União Estável'
        }
        return mapping.get(self.cliente.estado_civil, self.cliente.estado_civil or '')

    def _get_sexo(self):
        mapping = {'masculino': 'Masculino', 'feminino': 'Feminino', 'outro': 'Outro'}
        return mapping.get(self.cliente.sexo, self.cliente.sexo or '')

    # ==================== COMPONENTES ====================

    def _create_section_header(self, text, width):
        """Cria cabeçalho de seção com fundo dourado"""
        header_table = Table(
            [[Paragraph(text, self.styles['SectionHeader'])]],
            colWidths=[width]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_dourada),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return header_table

    def _create_field_cell(self, label, value, width=None):
        """Cria célula de campo com label e valor"""
        content = f"<font size='6'><b>{label}</b></font><br/><font size='8'>{value or ''}</font>"
        return Paragraph(content, ParagraphStyle(
            'FieldCell', fontSize=8, alignment=TA_LEFT, leading=10
        ))

    def _add_logo(self, elements, width_cm=5):
        """Adiciona logo centralizado mantendo proporção"""
        if os.path.exists(self.logo_path):
            # Proporção da logo HM Capital (1536x737 = 2.08:1)
            height_cm = width_cm / 2.08
            logo = Image(self.logo_path, width=width_cm*cm, height=height_cm*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            return True
        return False

    # ==================== PÁGINA 1: CAPA ====================

    def _create_cover_page(self, elements):
        """Cria página de capa profissional"""
        page_width = self.width - 3*cm

        # Espaço inicial
        elements.append(Spacer(1, 2.5*cm))

        # Logo grande centralizado (proporção correta da imagem HM Capital 2.08:1)
        if os.path.exists(self.logo_path):
            logo_width = 8*cm
            logo_height = logo_width / 2.08
            logo = Image(self.logo_path, width=logo_width, height=logo_height)
            logo.hAlign = 'CENTER'
            elements.append(logo)

        elements.append(Spacer(1, 1.5*cm))

        # Linha decorativa dourada
        line_table = Table([['']], colWidths=[12*cm], rowHeights=[3])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_dourada),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        line_table.hAlign = 'CENTER'
        elements.append(line_table)

        elements.append(Spacer(1, 1.5*cm))

        # Título principal
        elements.append(Paragraph("FICHA DE ATENDIMENTO", self.styles['CoverTitle']))
        elements.append(Paragraph("Planejamento Financeiro Personalizado", self.styles['CoverSubtitle']))

        elements.append(Spacer(1, 2*cm))

        # Nome do cliente em destaque
        elements.append(Paragraph(
            (self.cliente.nome or "CLIENTE").upper(),
            self.styles['ClienteName']
        ))

        elements.append(Spacer(1, 0.5*cm))

        # Linha decorativa dourada
        elements.append(line_table)

        elements.append(Spacer(1, 3*cm))

        # Texto motivacional
        elements.append(Paragraph(
            '"Traga seus sonhos, no seu tempo, e nós faremos acontecer!"',
            self.styles['MotivationalText']
        ))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            '"Dê o primeiro passo agora e transforme seu futuro em uma realidade de conquistas."',
            self.styles['MotivationalText']
        ))

        elements.append(Spacer(1, 3*cm))

        # Informações do representante (se houver)
        if self.representante:
            rep_info = f"Estrategista Financeiro: {self.representante.nome}"
            elements.append(Paragraph(rep_info, ParagraphStyle(
                'RepInfo', fontSize=11, alignment=TA_CENTER,
                textColor=self.cor_header, fontName='Helvetica-Bold'
            )))

        # Data
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(
            f"Data: {self.data_formatada}",
            self.styles['FooterText']
        ))

        elements.append(PageBreak())

    # ==================== PÁGINA 2: CADASTRO PESSOA FÍSICA ====================

    def _create_cadastro_page(self, elements):
        """Cria página de cadastro pessoa física"""
        page_width = self.width - 3*cm

        # Logo pequeno no topo
        if os.path.exists(self.logo_path):
            logo_width = 3*cm
            logo = Image(self.logo_path, width=logo_width, height=logo_width/2.08)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.2*cm))

        # Header principal verde
        header_table = Table(
            [[Paragraph("<b>CADASTRO PESSOA FÍSICA</b>", self.styles['PageHeader'])]],
            colWidths=[page_width]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_verde),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*cm))

        # ============ INFORMAÇÕES CADASTRAIS ============
        elements.append(self._create_section_header("INFORMAÇÕES CADASTRAIS", page_width))

        telefones = self._format_telefone(self.cliente.telefone)
        if self.cliente.telefone_secundario:
            telefones += f" / {self._format_telefone(self.cliente.telefone_secundario)}"

        # Estilo base de célula
        def get_cell_style(with_label_bg=True):
            styles = [
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 6.5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ]
            if with_label_bg:
                styles.append(('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro))
                styles.append(('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'))
            return TableStyle(styles)

        # Linha 1: Nome, Data Nasc, CPF
        row1 = [
            ['NOME COMPLETO', 'DATA DE NASCIMENTO', 'C.P.F.'],
            [self.cliente.nome or '', self._format_date(self.cliente.data_nascimento), self._format_cpf(self.cliente.cpf)]
        ]
        t1 = Table(row1, colWidths=[9*cm, 4*cm, 4.5*cm])
        t1.setStyle(get_cell_style())
        elements.append(t1)

        # Linha 2: Identidade, Expedidor, Emissão, Naturalidade, Nacionalidade
        row2 = [
            ['DOC. IDENTIDADE', 'EXPEDIDOR', 'EMISSÃO', 'NATURALIDADE', 'NACIONALIDADE'],
            [
                self.cliente.identidade or '',
                self.cliente.orgao_expedidor or '',
                self._format_date(self.cliente.data_expedicao),
                self.cliente.naturalidade or '',
                self.cliente.nacionalidade or 'Brasileira'
            ]
        ]
        t2 = Table(row2, colWidths=[4*cm, 2.5*cm, 2.5*cm, 4*cm, 4.5*cm])
        t2.setStyle(get_cell_style())
        elements.append(t2)

        # Linha 3: Nome da Mãe, Nome do Pai, N. CNH
        row3 = [
            ['NOME DA MÃE', 'NOME DO PAI', 'N. CNH (EM CASO DE VEÍCULOS)'],
            [self.cliente.nome_mae or '', self.cliente.nome_pai or '', '']
        ]
        t3 = Table(row3, colWidths=[6*cm, 6*cm, 5.5*cm])
        t3.setStyle(get_cell_style())
        elements.append(t3)

        # Linha 4: Estado Civil, Email, Sexo, Telefones
        row4 = [
            ['ESTADO CIVIL', 'E-MAIL', 'SEXO', 'TELEFONES'],
            [self._get_estado_civil(), self.cliente.email or '', self._get_sexo(), telefones]
        ]
        t4 = Table(row4, colWidths=[3.5*cm, 6.5*cm, 3*cm, 4.5*cm])
        t4.setStyle(get_cell_style())
        elements.append(t4)

        # Linha 5: Cônjuge (mesma estrutura das outras linhas)
        row5 = [
            ['NOME DO CÔNJUGE', 'DATA NASCIMENTO CÔNJUGE', 'CPF DO CÔNJUGE'],
            [
                self.cliente.conjuge_nome or '',
                self._format_date(self.cliente.conjuge_data_nascimento),
                self._format_cpf(self.cliente.conjuge_cpf)
            ]
        ]
        t5 = Table(row5, colWidths=[9*cm, 4*cm, 4.5*cm])
        t5.setStyle(get_cell_style())
        elements.append(t5)

        elements.append(Spacer(1, 0.15*cm))

        # ============ INFORMAÇÕES RESIDENCIAIS ============
        elements.append(self._create_section_header("INFORMAÇÕES RESIDENCIAIS", page_width))

        # Linha 1: Endereço, Número, Complemento, CEP
        row_res1 = [
            ['ENDEREÇO RESIDENCIAL', 'NÚMERO', 'COMPLEMENTO', 'CEP'],
            [self.cliente.logradouro or '', self.cliente.numero or '', self.cliente.complemento or '', self._format_cep(self.cliente.cep)]
        ]
        t_res1 = Table(row_res1, colWidths=[8*cm, 2.5*cm, 4*cm, 3*cm])
        t_res1.setStyle(get_cell_style())
        elements.append(t_res1)

        # Linha 2: Bairro, Cidade, UF, Tipo Residência, Tempo Residência
        row_res2 = [
            ['BAIRRO', 'CIDADE', 'UF', 'TIPO DE RESIDÊNCIA', 'TEMPO DE RESIDÊNCIA'],
            [self.cliente.bairro or '', self.cliente.cidade or '', self.cliente.estado or '', '', '']
        ]
        t_res2 = Table(row_res2, colWidths=[4*cm, 5*cm, 1.5*cm, 4*cm, 3*cm])
        t_res2.setStyle(get_cell_style())
        elements.append(t_res2)

        elements.append(Spacer(1, 0.15*cm))

        # ============ INFORMAÇÕES PROFISSIONAIS ============
        elements.append(self._create_section_header("INFORMAÇÕES PROFISSIONAIS", page_width))

        # Linha 1: Empresa (larguras iguais à linha 2 para alinhamento)
        row_prof1 = [
            ['EMPRESA ONDE TRABALHA', 'CNPJ', 'RAMO DE ATIVIDADE', 'TEMPO'],
            [self.cliente.empresa_trabalho or '', '', '', '']
        ]
        t_prof1 = Table(row_prof1, colWidths=[8*cm, 2.5*cm, 4*cm, 3*cm])
        t_prof1.setStyle(get_cell_style())
        elements.append(t_prof1)

        # Linha 2: Endereço comercial (campos vazios)
        row_prof2 = [
            ['ENDEREÇO', 'NÚMERO', 'COMPLEMENTO', 'CEP'],
            ['', '', '', '']
        ]
        t_prof2 = Table(row_prof2, colWidths=[8*cm, 2.5*cm, 4*cm, 3*cm])
        t_prof2.setStyle(get_cell_style())
        elements.append(t_prof2)

        # Linha 3: Bairro, Cidade, UF, Telefones comerciais
        row_prof3 = [
            ['BAIRRO', 'CIDADE', 'UF', 'TELEFONE 1', 'TELEFONE 2'],
            ['', '', '', '', '']
        ]
        t_prof3 = Table(row_prof3, colWidths=[4*cm, 4*cm, 1.5*cm, 4*cm, 4*cm])
        t_prof3.setStyle(get_cell_style())
        elements.append(t_prof3)

        # Linha 4: Profissão, Admissão, CNPJ, Renda, Outras Rendas, Total
        renda = self._format_currency(self.cliente.salario)
        row_prof4 = [
            ['PROFISSÃO/CARGO', 'DATA DE ADMISSÃO', 'CNPJ DA EMPRESA', 'RENDA MENSAL', 'OUTRAS RENDAS', 'TOTAL'],
            [self.cliente.cargo or '', '', '', renda, '', renda]
        ]
        t_prof4 = Table(row_prof4, colWidths=[4*cm, 3*cm, 3.5*cm, 3*cm, 2.5*cm, 1.5*cm])
        t_prof4.setStyle(get_cell_style())
        elements.append(t_prof4)

        elements.append(Spacer(1, 0.15*cm))

        # ============ INFORMAÇÕES PARA ANÁLISE DE CRÉDITO ============
        elements.append(self._create_section_header("INFORMAÇÕES PARA ANÁLISE DE CRÉDITO", page_width))

        def sim_nao(valor):
            return 'Sim' if valor else ''

        def prazo_str(prazo):
            return str(prazo) if prazo else ''

        def valor_str(valor):
            return self._format_currency(valor) if valor else ''

        # Tabela de compromissos
        comp_data = [
            ['COMPROMISSOS FINANCEIROS', 'POSSUI?', 'PRAZO', 'VALOR'],
            ['Consórcio', sim_nao(self.cliente.tem_consorcio), prazo_str(self.cliente.consorcio_prazo), valor_str(self.cliente.consorcio_valor)],
            ['Empréstimos no Contracheque', sim_nao(self.cliente.tem_emprestimo_contracheque), prazo_str(self.cliente.emprestimo_contracheque_prazo), valor_str(self.cliente.emprestimo_contracheque_valor)],
            ['Empréstimos, Leasing, CDC, Crediário', sim_nao(self.cliente.tem_emprestimo_outros), prazo_str(self.cliente.emprestimo_outros_prazo), valor_str(self.cliente.emprestimo_outros_valor)],
            ['Financiamento Estudantil', sim_nao(self.cliente.tem_financiamento_estudantil), prazo_str(self.cliente.financiamento_estudantil_prazo), valor_str(self.cliente.financiamento_estudantil_valor)],
            ['Financiamento Veicular', sim_nao(self.cliente.tem_financiamento_veicular), prazo_str(self.cliente.financiamento_veicular_prazo), valor_str(self.cliente.financiamento_veicular_valor)],
            ['Financiamento Habitacional', sim_nao(self.cliente.tem_financiamento_habitacional), prazo_str(self.cliente.financiamento_habitacional_prazo), valor_str(self.cliente.financiamento_habitacional_valor)],
            ['Aluguel', sim_nao(self.cliente.tem_aluguel), '', valor_str(self.cliente.aluguel_valor)],
            ['Outras Dívidas Não Declaradas', sim_nao(self.cliente.tem_outras_dividas), '', valor_str(self.cliente.outras_dividas_valor)],
        ]

        t_comp = Table(comp_data, colWidths=[8*cm, 2.5*cm, 3*cm, 4*cm])
        t_comp.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 6.5),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ]))
        elements.append(t_comp)

        # Linha de restrições
        possui_restricao = 'Sim' if self.cliente.possui_restricao else 'Não'
        tentou_credito = 'Sim' if self.cliente.tentou_credito_12_meses else 'Não'

        rest_data = [
            ['POSSUI RESTRIÇÃO?', 'PROTESTOS?', 'TENTOU OBTER CRÉDITO NOS ÚLTIMOS 12 MESES?', 'QUAL INSTITUIÇÃO?'],
            [possui_restricao, '', tentou_credito, '']
        ]
        t_rest = Table(rest_data, colWidths=[4*cm, 3*cm, 7*cm, 3.5*cm])
        t_rest.setStyle(get_cell_style())
        elements.append(t_rest)

        elements.append(Spacer(1, 0.15*cm))

        # ============ OBSERVAÇÕES ============
        elements.append(self._create_section_header("OBSERVAÇÕES", page_width))

        obs_text = self.cliente.observacoes or ''
        obs_table = Table([[obs_text]], colWidths=[page_width], rowHeights=[0.8*cm])
        obs_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(obs_table)

        elements.append(PageBreak())

    # ==================== PÁGINA 3: TERMO DE USO ====================

    def _create_termo_uso_page(self, elements):
        """Cria página do Termo de Uso para Análise de Perfil Financeiro"""
        page_width = self.width - 3*cm

        # Logo pequeno no topo
        if os.path.exists(self.logo_path):
            logo_width = 3.5*cm
            logo = Image(self.logo_path, width=logo_width, height=logo_width/2.08)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.3*cm))

        # Header principal verde
        header_table = Table(
            [[Paragraph("<b>TERMO DE USO PARA ANÁLISE DE PERFIL FINANCEIRO<br/>PARA LINHAS DE CRÉDITO</b>",
                ParagraphStyle('TermoHeader', fontSize=12, alignment=TA_CENTER,
                    textColor=colors.white, fontName='Helvetica-Bold', leading=15)
            )]],
            colWidths=[page_width]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_verde),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.5*cm))

        # Estilo para título de seção
        termo_section_style = ParagraphStyle(
            'TermoSection', fontSize=10, fontName='Helvetica-Bold',
            textColor=self.cor_verde, leading=13, spaceBefore=4, spaceAfter=2
        )

        # Estilo para texto do termo
        termo_text_style = ParagraphStyle(
            'TermoText', fontSize=9.5, fontName='Helvetica',
            alignment=TA_JUSTIFY, leading=13, spaceAfter=4
        )

        sections = [
            ("1. Processo de análise",
             "Estes termos de uso estabelecem os direitos e as responsabilidades do cliente e da empresa HM Capital, "
             "no processo para as linhas de crédito para financiamentos, carta de crédito contemplada ou consórcio, "
             "em grupos, bancos e financeiras fiscalizadas pelo Banco Central. Ao utilizar os serviços da empresa, "
             "você concorda que está de acordo com os termos de uso e autoriza a empresa a consultar o CPF nos "
             "órgãos de proteção ao crédito."),

            ("2. Solicitação de Crédito",
             "Na solicitação de uma linha de crédito, o cliente deve estar ciente que deve fornecer informações "
             "precisas e atualizadas por meio de formulário de CADASTRO fornecido pela empresa. O cliente é o "
             "único responsável pela precisão e integridade das informações fornecidas."),

            ("3. Consentimento para Análise de Crédito",
             "Ao assinar este termo, o cliente consente explicitamente que a empresa realize a análise de crédito, "
             "incluindo a coleta, o processamento e o armazenamento de informações pessoais relevantes, como o "
             "número de CPF (Cadastro de Pessoa Física), conforme necessário avaliar a elegibilidade do cliente "
             "para linha de crédito solicitada."),

            ("4. Verificação das Informações",
             "A empresa reserva o direito de verificar as informações fornecidas pelo cliente com terceiros, "
             "incluindo instituições financeiras, órgãos de crédito e outras fontes relevantes. Essa verificação "
             "pode incluir a consulta de registros de crédito e a validação do número de CPF fornecido pelo cliente."),

            ("5. Avaliação de Crédito",
             "Com base nas informações fornecidas pelo cliente e nos resultados de verificação, a empresa realizará "
             "uma avaliação de crédito para determinar a elegibilidade do cliente para a linha de crédito de "
             "financiamento, consórcios, cartas de crédito contempladas e demais linhas solicitadas pelo cliente "
             "ou oferecidas como opção viável para o cliente. A empresa reserva o direito de aceitar ou recusar "
             "qualquer solicitação de crédito de acordo com os critérios internos."),

            ("6. Privacidade e Segurança - LEI GERAL DE PROTEÇÃO DE DADOS (LGPD)",
             "A empresa cumprirá integralmente as disposições da Lei Geral de Proteção de Dados (Lei 13.709/2018), "
             "completa ao processamento de informações pessoais do cliente. A coleta, o processamento e o "
             "armazenamento de dados serão realizados de acordo com as finalidades específicas de análise de "
             "crédito e demais obrigações legais."),

            ("7. Disposições Gerais - Alterações nos Termos de Uso",
             "A empresa se reserva o direito de modificar estes Termos de Uso a qualquer momento, mediante aviso "
             "prévio adequado ao cliente. Recomenda-se que o cliente revise regularmente os termos utilizados."),
        ]

        for title, text in sections:
            elements.append(Paragraph(f"<b>{title}</b>", termo_section_style))
            elements.append(Paragraph(text, termo_text_style))
            elements.append(Spacer(1, 0.15*cm))

        # Parágrafo final
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(
            "Ao aceitar com o processo de análise de crédito, o cliente confirma que leu, entendeu e concorda "
            "com estes Termos de Uso. Em caso de dúvidas ou preocupações, o cliente deve perguntar ao "
            "representante da empresa para obter os esclarecimentos adicionais.",
            ParagraphStyle(
                'TermoFinal', fontSize=9.5, fontName='Helvetica-Bold',
                alignment=TA_JUSTIFY, leading=13, spaceAfter=6
            )
        ))

        elements.append(Spacer(1, 1.5*cm))

        # Data e Assinatura
        sig_data = [
            ['DATA: ___________________________', '', 'ASSINATURA DO CLIENTE: ___________________________'],
        ]
        sig_table = Table(sig_data, colWidths=[7*cm, 3.5*cm, 7*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(sig_table)

        elements.append(PageBreak())

    # ==================== PÁGINA 4: PROPOSTA DE ORÇAMENTO ====================

    def _create_proposta_page(self, elements):
        """Cria página de proposta de orçamento com 4 propostas"""
        page_width = self.width - 3*cm

        # Logo pequeno no topo
        if os.path.exists(self.logo_path):
            logo_width = 4*cm
            logo = Image(self.logo_path, width=logo_width, height=logo_width/2.08)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.3*cm))

        # Header da proposta
        header_table = Table(
            [[
                Paragraph("<b>PROPOSTA<br/>DE ORÇAMENTO</b>", ParagraphStyle(
                    'PropostaHeader', fontSize=16, textColor=colors.white,
                    alignment=TA_LEFT, leading=20, fontName='Helvetica-Bold'
                )),
                Paragraph("<b>HM.CAPITAL</b>", ParagraphStyle(
                    'PropostaHeaderRight', fontSize=11, textColor=self.cor_dourada,
                    alignment=TA_RIGHT, fontName='Helvetica-Bold'
                ))
            ]],
            colWidths=[10*cm, page_width - 10*cm]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_verde),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (0, 0), 15),
            ('RIGHTPADDING', (1, 0), (1, 0), 15),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.8*cm))

        # 4 Propostas em grid 2x2
        half_width = (page_width - 0.5*cm) / 2

        def make_proposta(num_romano):
            title_style = ParagraphStyle(
                'PropTitle', fontSize=11, fontName='Helvetica-Bold',
                alignment=TA_LEFT, textColor=self.cor_verde, leading=14
            )
            content_style = ParagraphStyle(
                'PropContent', fontSize=9, fontName='Helvetica',
                spaceAfter=3, leading=16, textColor=colors.HexColor('#333333')
            )

            content = [
                [Paragraph(f"<b>Proposta {num_romano}</b>  ({'&nbsp;' * 35})", title_style)],
                [Paragraph("Crédito Pretendido: ____________________", content_style)],
                [Paragraph("Entrada Sugerida: ____________________", content_style)],
                [Paragraph("Parcelas a partir: ____________________", content_style)],
                [Paragraph("Prazos Aproximados: ____________________", content_style)],
            ]

            t = Table(content, colWidths=[half_width - 0.5*cm])
            t.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (0, 0), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            return t

        # Linha 1 de propostas
        row1 = Table([[make_proposta('I'), make_proposta('II')]], colWidths=[half_width, half_width])
        row1.setStyle(TableStyle([
            ('BOX', (0, 0), (0, 0), 1, self.cor_dourada),
            ('BOX', (1, 0), (1, 0), 1, self.cor_dourada),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(row1)

        elements.append(Spacer(1, 0.3*cm))

        # Linha 2 de propostas
        row2 = Table([[make_proposta('III'), make_proposta('IV')]], colWidths=[half_width, half_width])
        row2.setStyle(TableStyle([
            ('BOX', (0, 0), (0, 0), 1, self.cor_dourada),
            ('BOX', (1, 0), (1, 0), 1, self.cor_dourada),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(row2)
        elements.append(Spacer(1, 0.5*cm))

        # Observações
        elements.append(Paragraph("<b>OBSERVAÇÕES</b>", ParagraphStyle(
            'ObsTitle', fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#333333')
        )))
        elements.append(Spacer(1, 0.15*cm))

        obs_box = Table([['  ']], colWidths=[page_width], rowHeights=[4*cm])
        obs_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#666666')),
        ]))
        elements.append(obs_box)
        elements.append(Spacer(1, 0.3*cm))

        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer', fontSize=7, alignment=TA_JUSTIFY,
            leading=9, fontName='Helvetica', textColor=colors.HexColor('#888888')
        )
        elements.append(Paragraph(
            "Declaro ter consciência que a análise de crédito realizada na data de hoje pode resultar na aprovação ou "
            "reprovação do crédito com base nas informações fornecidas na simulação. O cliente reconhece que as condições "
            "atuais podem mudar ao longo do tempo devido a alterações em sua situação pessoal, como renda, profissão, "
            "estado civil, entre outros. Também está ciente de que o status de aprovação ou reprovação pode ser revisado "
            "a qualquer momento.",
            disclaimer_style
        ))

        elements.append(Spacer(1, 0.6*cm))

        # Assinatura
        sig_data = [
            ['________________________', self.data_formatada, '________________________'],
            ['LOCAL', 'DATA', 'ASSINATURA DO CLIENTE'],
        ]
        sig_table = Table(sig_data, colWidths=[5.5*cm, 4*cm, 5.5*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, 1), 8),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#555555')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(sig_table)

    # ==================== GERAÇÃO DO PDF ====================

    def _draw_cover_border(self, canvas_obj, doc):
        """Desenha borda dourada dupla na página de capa"""
        canvas_obj.saveState()
        w, h = A4
        margin = 1*cm

        # Borda externa dourada
        canvas_obj.setStrokeColor(self.cor_dourada)
        canvas_obj.setLineWidth(2.5)
        canvas_obj.rect(margin, margin, w - 2*margin, h - 2*margin)

        # Borda interna dourada (dupla)
        canvas_obj.setLineWidth(0.75)
        inner = margin + 4*mm
        canvas_obj.rect(inner, inner, w - 2*inner, h - 2*inner)

        canvas_obj.restoreState()

    def generate(self):
        """Gera o PDF completo e retorna os bytes"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = []

        # Página 1: Capa
        self._create_cover_page(elements)

        # Página 2: Cadastro Pessoa Física
        self._create_cadastro_page(elements)

        # Página 3: Termo de Uso
        self._create_termo_uso_page(elements)

        # Página 4: Proposta de Orçamento
        self._create_proposta_page(elements)

        # Controla qual página está sendo desenhada
        self._page_num = 0

        def on_page(canvas_obj, doc):
            self._page_num += 1
            if self._page_num == 1:
                self._draw_cover_border(canvas_obj, doc)

        doc.build(elements, onFirstPage=on_page, onLaterPages=lambda c, d: None)
        buffer.seek(0)
        return buffer.getvalue()

    def get_filename(self):
        """Retorna o nome do arquivo sugerido"""
        nome_limpo = (self.cliente.nome or 'cliente').replace(' ', '_').lower()
        nome_limpo = ''.join(c for c in nome_limpo if c.isalnum() or c == '_')
        data_str = self.data_atual.strftime("%Y%m%d")
        return f"ficha_cliente_{nome_limpo}_{data_str}.pdf"
