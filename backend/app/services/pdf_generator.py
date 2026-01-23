"""
Serviço de geração de PDF - Ficha de Atendimento
Baseado no modelo Siprov/Uni+
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os


class ClientePDFGenerator:
    def __init__(self, cliente, beneficio=None, tabelas_simulacao=None):
        self.cliente = cliente
        self.beneficio = beneficio
        self.tabelas_simulacao = tabelas_simulacao or []
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()

        # Cores do tema
        self.cor_dourada = colors.HexColor('#C4A962')
        self.cor_header = colors.HexColor('#3D3D3D')
        self.cor_cinza_claro = colors.HexColor('#F5F5F5')

        # Caminho do logo
        self.logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo-white-bg.jpg')

    def _setup_styles(self):
        """Configura estilos customizados"""
        self.styles.add(ParagraphStyle(
            name='ClienteName',
            fontSize=22,
            alignment=TA_CENTER,
            spaceAfter=5,
            spaceBefore=0,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='MainTitle',
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=5,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SubTitle',
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CenterText',
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=5,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='CenterTextBold',
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SmallCenter',
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=3,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='JustifyText',
            fontSize=9,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=12,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='TableLabel',
            fontSize=7,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='TableValue',
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica'
        ))

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
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        return header_table

    def _create_cover_page(self, elements):
        """Cria página de capa"""
        # Espaço inicial
        elements.append(Spacer(1, 2*cm))

        # Logo ou nome da empresa
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=6*cm, height=2.25*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
        else:
            elements.append(Paragraph("HM CAPITAL", self.styles['ClienteName']))

        elements.append(Spacer(1, 4*cm))

        # Nome do cliente
        elements.append(Paragraph(self.cliente.nome.upper(), self.styles['ClienteName']))

        # Linha separadora
        elements.append(Spacer(1, 0.3*cm))
        line_data = [['_' * 50]]
        line_table = Table(line_data, colWidths=[12*cm])
        line_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.5*cm))

        # Títulos principais
        elements.append(Paragraph("PLANEJAMENTO FINANCEIRO", self.styles['MainTitle']))
        elements.append(Paragraph("ORÇAMENTO PERSONALIZADO", self.styles['SubTitle']))

        elements.append(Spacer(1, 5*cm))

        # Linha separadora
        elements.append(line_table)
        elements.append(Spacer(1, 0.5*cm))

        # Estrategista
        elements.append(Paragraph("Estrategista Financeiro", self.styles['CenterTextBold']))

        elements.append(Spacer(1, 1.5*cm))

        # Texto motivacional
        elements.append(Paragraph(
            "<b>Traga seus sonhos, no seu tempo, e nós faremos sucesso!</b>",
            self.styles['CenterTextBold']
        ))
        elements.append(Paragraph(
            "<b>Dê o primeiro passo agora e transforme seu futuro em uma realidade de conquistas.</b>",
            self.styles['CenterTextBold']
        ))

        elements.append(PageBreak())

    def _create_cadastro_page(self, elements):
        """Cria página de cadastro - tudo em uma página"""
        page_width = self.width - 3*cm

        # Logo no topo
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=3*cm, height=1.1*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.2*cm))

        # Header principal
        header_table = Table(
            [[Paragraph("<b>CADASTRO PESSOA FÍSICA</b>", ParagraphStyle(
                'HeaderTitle', fontSize=14, textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold'
            ))]],
            colWidths=[page_width]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_header),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.3*cm))

        # ============ INFORMAÇÕES CADASTRAIS ============
        elements.append(self._create_section_header("INFORMAÇÕES CADASTRAIS", page_width))

        telefones = self._format_telefone(self.cliente.telefone)
        if self.cliente.telefone_secundario:
            telefones += f" / {self._format_telefone(self.cliente.telefone_secundario)}"

        # Linha 1: Nome, Data Nasc, CPF
        row1_labels = [['NOME COMPLETO', '', 'DATA DE NASCIMENTO', 'C.P.F.']]
        row1_values = [[self.cliente.nome or '', '', self._format_date(self.cliente.data_nascimento), self._format_cpf(self.cliente.cpf)]]

        # Linha 2: Identidade, Expedidor, Emissão, Naturalidade, Nacionalidade
        row2_labels = [['DOC. IDENTIDADE', 'EXPEDIDOR', 'EMISSÃO', 'NATURALIDADE', 'NACIONALIDADE']]
        row2_values = [[
            self.cliente.identidade or '',
            self.cliente.orgao_expedidor or '',
            self._format_date(self.cliente.data_expedicao),
            self.cliente.naturalidade or '',
            self.cliente.nacionalidade or 'Brasileira'
        ]]

        # Linha 3: Nome da Mãe, Nome do Pai
        row3_labels = [['NOME DA MÃE', '', 'NOME DO PAI', '']]
        row3_values = [[self.cliente.nome_mae or '', '', self.cliente.nome_pai or '', '']]

        # Linha 4: Estado Civil, Email, Sexo, Telefones
        estado_civil_map = {
            'solteiro': 'Solteiro(a)', 'casado': 'Casado(a)', 'divorciado': 'Divorciado(a)',
            'viuvo': 'Viúvo(a)', 'uniao_estavel': 'União Estável'
        }
        sexo_map = {'masculino': 'Masculino', 'feminino': 'Feminino', 'outro': 'Outro'}

        row4_labels = [['ESTADO CIVIL', 'E-MAIL', 'SEXO', 'TELEFONES']]
        row4_values = [[
            estado_civil_map.get(self.cliente.estado_civil, self.cliente.estado_civil or ''),
            self.cliente.email or '',
            sexo_map.get(self.cliente.sexo, self.cliente.sexo or ''),
            telefones
        ]]

        # Linha 5: Cônjuge
        row5_labels = [['NOME DO CÔNJUGE', '', '', '']]
        row5_values = [[self.cliente.conjuge_nome or '', '', '', '']]

        col_widths = [4.5*cm, 4*cm, 4.5*cm, 4.5*cm]
        col_widths_5 = [3.5*cm, 3.2*cm, 3.2*cm, 3.6*cm, 4*cm]

        cadastro_data = []
        cadastro_data.extend(row1_labels)
        cadastro_data.extend(row1_values)
        cadastro_data.extend(row2_labels)
        cadastro_data.extend(row2_values)
        cadastro_data.extend(row3_labels)
        cadastro_data.extend(row3_values)
        cadastro_data.extend(row4_labels)
        cadastro_data.extend(row4_values)
        cadastro_data.extend(row5_labels)
        cadastro_data.extend(row5_values)

        cadastro_table = Table(cadastro_data, colWidths=col_widths)
        cadastro_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
            ('FONTNAME', (0, 8), (-1, 8), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_cinza_claro),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_cinza_claro),
            ('BACKGROUND', (0, 6), (-1, 6), self.cor_cinza_claro),
            ('BACKGROUND', (0, 8), (-1, 8), self.cor_cinza_claro),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('SPAN', (0, 0), (1, 0)), ('SPAN', (0, 1), (1, 1)),
            ('SPAN', (2, 4), (3, 4)), ('SPAN', (2, 5), (3, 5)),
            ('SPAN', (0, 8), (3, 8)), ('SPAN', (0, 9), (3, 9)),
        ]))
        elements.append(cadastro_table)
        elements.append(Spacer(1, 0.2*cm))

        # ============ INFORMAÇÕES RESIDENCIAIS ============
        elements.append(self._create_section_header("INFORMAÇÕES RESIDENCIAIS", page_width))

        endereco = f"{self.cliente.logradouro or ''}, {self.cliente.numero or ''}, {self.cliente.bairro or ''}, {self.cliente.cidade or ''} - {self.cliente.estado or ''}, {self.cliente.cep or ''}"

        res_data = [
            ['ENDEREÇO RESIDENCIAL', 'NÚMERO', 'COMPLEMENTO', 'CEP'],
            [endereco[:60], self.cliente.numero or '', self.cliente.complemento or '', self.cliente.cep or ''],
            ['BAIRRO', 'CIDADE', 'UF', 'TIPO DE RESIDÊNCIA'],
            [self.cliente.bairro or '', self.cliente.cidade or '', self.cliente.estado or '', ''],
        ]

        res_table = Table(res_data, colWidths=[7*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        res_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_cinza_claro),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(res_table)
        elements.append(Spacer(1, 0.2*cm))

        # ============ INFORMAÇÕES PROFISSIONAIS ============
        elements.append(self._create_section_header("INFORMAÇÕES PROFISSIONAIS", page_width))

        prof_data = [
            ['EMPRESA ONDE TRABALHA', 'PROFISSÃO/CARGO', 'RENDA MENSAL'],
            [self.cliente.empresa_trabalho or '', self.cliente.cargo or '', self._format_currency(self.cliente.salario)],
        ]

        prof_table = Table(prof_data, colWidths=[7*cm, 5.5*cm, 5*cm])
        prof_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(prof_table)
        elements.append(Spacer(1, 0.2*cm))

        # ============ INFORMAÇÕES PARA ANÁLISE DE CRÉDITO ============
        elements.append(self._create_section_header("INFORMAÇÕES PARA ANÁLISE DE CRÉDITO", page_width))

        def get_possui(tem):
            return 'Sim' if tem else ''

        def get_prazo(prazo):
            return str(prazo) if prazo else ''

        def get_valor(valor):
            return self._format_currency(valor) if valor else ''

        comp_data = [
            ['COMPROMISSOS FINANCEIROS', 'POSSUI?', 'PRAZO', 'VALOR'],
            ['CONSÓRCIO', get_possui(self.cliente.tem_consorcio), get_prazo(self.cliente.consorcio_prazo), get_valor(self.cliente.consorcio_valor)],
            ['EMPRÉSTIMOS NO CONTRACHEQUE', get_possui(self.cliente.tem_emprestimo_contracheque), get_prazo(self.cliente.emprestimo_contracheque_prazo), get_valor(self.cliente.emprestimo_contracheque_valor)],
            ['EMPRÉSTIMOS, LEASING, CDC, CREDIÁRIO', get_possui(self.cliente.tem_emprestimo_outros), get_prazo(self.cliente.emprestimo_outros_prazo), get_valor(self.cliente.emprestimo_outros_valor)],
            ['FINANCIAMENTO ESTUDANTIL', get_possui(self.cliente.tem_financiamento_estudantil), get_prazo(self.cliente.financiamento_estudantil_prazo), get_valor(self.cliente.financiamento_estudantil_valor)],
            ['FINANCIAMENTO VEICULAR', get_possui(self.cliente.tem_financiamento_veicular), get_prazo(self.cliente.financiamento_veicular_prazo), get_valor(self.cliente.financiamento_veicular_valor)],
            ['FINANCIAMENTO HABITACIONAL', get_possui(self.cliente.tem_financiamento_habitacional), get_prazo(self.cliente.financiamento_habitacional_prazo), get_valor(self.cliente.financiamento_habitacional_valor)],
            ['ALUGUEL', get_possui(self.cliente.tem_aluguel), '', get_valor(self.cliente.aluguel_valor)],
            ['OUTRAS DÍVIDAS NÃO DECLARADAS', get_possui(self.cliente.tem_outras_dividas), '', get_valor(self.cliente.outras_dividas_valor)],
        ]

        comp_table = Table(comp_data, colWidths=[8*cm, 3*cm, 3*cm, 3.5*cm])
        comp_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(comp_table)

        # Linha de restrições
        rest_data = [
            ['POSSUI RESTRIÇÃO?', 'PROTESTOS?', 'TENTOU OBTER CRÉDITO NOS ÚLTIMOS 12 MESES?', 'QUAL INSTITUIÇÃO?'],
            ['Sim' if self.cliente.possui_restricao else 'Não', '', 'Sim' if self.cliente.tentou_credito_12_meses else 'Não', ''],
        ]

        rest_table = Table(rest_data, colWidths=[4.5*cm, 3.5*cm, 6.5*cm, 3*cm])
        rest_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_cinza_claro),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(rest_table)
        elements.append(Spacer(1, 0.2*cm))

        # ============ OBSERVAÇÕES ============
        elements.append(self._create_section_header("OBSERVAÇÕES", page_width))

        obs_text = self.cliente.observacoes or ''
        obs_table = Table([[obs_text]], colWidths=[page_width], rowHeights=[1.5*cm])
        obs_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(obs_table)
        elements.append(Spacer(1, 0.2*cm))

        # ============ SIMULAÇÃO ============
        elements.append(self._create_section_header("SIMULAÇÃO", page_width))

        tabelas = self.tabelas_simulacao[:3] if self.tabelas_simulacao else []

        sim_col_width = page_width / 3

        def make_sim_content(num, tabela=None):
            if tabela:
                return [
                    [Paragraph(f"<b>SIMULAÇÃO {num}</b>", ParagraphStyle('SimTitle', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
                    [f"Crédito Pretendido: {self._format_currency(tabela.valor_credito)}"],
                    [f"Entrada Sugerida: "],
                    [f"Parcelas a partir: {self._format_currency(tabela.parcela)}"],
                    [f"Prazos Aproximados: {tabela.prazo} meses"],
                ]
            else:
                return [
                    [Paragraph(f"<b>SIMULAÇÃO {num}</b>", ParagraphStyle('SimTitle', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
                    ["Crédito Pretendido:"],
                    ["Entrada Sugerida:"],
                    ["Parcelas a partir:"],
                    ["Prazos Aproximados:"],
                ]

        sim1 = make_sim_content(1, tabelas[0] if len(tabelas) > 0 else None)
        sim2 = make_sim_content(2, tabelas[1] if len(tabelas) > 1 else None)
        sim3 = make_sim_content(3, tabelas[2] if len(tabelas) > 2 else None)

        sim_table1 = Table(sim1, colWidths=[sim_col_width - 0.3*cm])
        sim_table2 = Table(sim2, colWidths=[sim_col_width - 0.3*cm])
        sim_table3 = Table(sim3, colWidths=[sim_col_width - 0.3*cm])

        for t in [sim_table1, sim_table2, sim_table3]:
            t.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

        sim_row = Table([[sim_table1, sim_table2, sim_table3]], colWidths=[sim_col_width, sim_col_width, sim_col_width])
        sim_row.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(sim_row)
        elements.append(Spacer(1, 0.5*cm))

        # Assinatura
        self._add_signature_section(elements)

        # Texto do termo
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            "<b>Termo de uso para Análise de Perfil Financeiro para Linhas de Crédito</b>",
            ParagraphStyle('TermoRef', fontSize=8, alignment=TA_CENTER, fontName='Helvetica-Bold')
        ))

        elements.append(PageBreak())

    def _create_terms_page(self, elements):
        """Cria página de termos de uso"""

        terms_style = ParagraphStyle('TermsTitle', fontSize=10, fontName='Helvetica-Bold', spaceAfter=5)
        terms_text = ParagraphStyle('TermsText', fontSize=9, alignment=TA_JUSTIFY, leading=12, spaceAfter=10, fontName='Helvetica')

        elements.append(Paragraph("1. Processo de análise", terms_style))
        elements.append(Paragraph(
            "Estes termos de uso estabelecem os direitos e as responsabilidades do cliente e da empresa HM Capital, no "
            "processo para as linhas de crédito para de financiamentos, carta de crédito contemplada ou consórcio, em "
            "grupos, bancos e financeiras fiscalizadas pelo Banco Central. Ao utilizar os serviços da empresa, você "
            "concorda que está de acordo com os termos de uso e autoriza a empresa a consultar o CPF nos órgãos de "
            "proteção ao crédito.",
            terms_text
        ))

        elements.append(Paragraph("2. Solicitação de Crédito", terms_style))
        elements.append(Paragraph(
            "Na solicitação de uma linha de crédito, o cliente deve estar ciente que deve fornecer informações precisas "
            "e atualizadas por meio de formulário de CADASTRO fornecido pela empresa. O cliente é o único "
            "responsável pela precisão e integridade das informações fornecidas.",
            terms_text
        ))

        elements.append(Paragraph("3. Consentimento para Análise de Crédito", terms_style))
        elements.append(Paragraph(
            "Ao assinar este termo, o cliente consente explicitamente que a empresa realize a análise de crédito, "
            "incluindo a coleta, o processamento e o armazenamento de informações pessoais relevantes, como o "
            "número de CPF (Cadastro de Pessoa Física), conforme necessário avaliar a elegibilidade do cliente para "
            "linha de crédito solicitada.",
            terms_text
        ))

        elements.append(Paragraph("4. Verificação das Informações", terms_style))
        elements.append(Paragraph(
            "A empresa reserva o direito de verificar as informações fornecidas pelo cliente com terceiros, incluindo "
            "instituições financeiras, órgãos de crédito e outras fontes relevantes. Essa verificação pode incluir a "
            "consulta de registros de crédito e a validação do número de CPF fornecido pelo cliente.",
            terms_text
        ))

        elements.append(Paragraph("5. Avaliação de Crédito", terms_style))
        elements.append(Paragraph(
            "Com base nas informações fornecidas pelo cliente e nos resultados de verificação, a empresa realizará uma "
            "avaliação de crédito para determinar a elegibilidade do cliente para a linha de crédito de financiamento, "
            "consórcios, cartas de crédito contempladas e demais linhas solicitadas pelo cliente ou oferecidas como "
            "opção viável para o cliente. A empresa reserva o direito de aceitar ou recusar qualquer solicitação de "
            "crédito de acordo com os critérios internos.",
            terms_text
        ))

        elements.append(Paragraph("6. Privacidade e Segurança - LEI GERAL DE PROTEÇÃO DE DADOS (LGPD)", terms_style))
        elements.append(Paragraph(
            "A empresa cumprirá integralmente as disposições da Lei Geral de Proteção de Dados (Lei. 13.709/2018), "
            "completa ao processamento de informações pessoais do cliente. A coleta, o processamento, e "
            "armazenamento de dados serão realizados de acordo com as finalidades específicas de análise de crédito e "
            "demais obrigações legais.",
            terms_text
        ))

        elements.append(Paragraph("7. Disposições Gerais - Alterações nos Termos de Uso", terms_style))
        elements.append(Paragraph(
            "A empresa se reserva o direito de modificar estes Termos de Uso a qualquer momento, mediante aviso "
            "prévio adequado ao cliente. Recomenda-se que o cliente revise regularmente os termos utilizados.",
            terms_text
        ))

        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            "Ao aceitar com o processo de análise de crédito, o cliente confirma que leu, entendeu e concorda com "
            "estes Termos de Uso. Em caso de dúvidas ou preocupações, o cliente deve perguntar ao representante da "
            "empresa para obter os esclarecimentos adicionais.",
            terms_text
        ))

        elements.append(Spacer(1, 2*cm))
        self._add_signature_section(elements)

        elements.append(PageBreak())

    def _create_proposal_page(self, elements):
        """Cria página de proposta de orçamento"""
        page_width = self.width - 3*cm

        # Logo no topo da página de proposta
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=4*cm, height=1.5*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.3*cm))

        # Header
        header_table = Table(
            [[Paragraph("<b>PROPOSTA<br/>DE ORÇAMENTO</b>", ParagraphStyle(
                'PropostaHeader', fontSize=20, textColor=colors.white, alignment=TA_LEFT, leading=24, fontName='Helvetica-Bold'
            )), Paragraph("<b>HM CAPITAL</b>", ParagraphStyle(
                'PropostaHeaderRight', fontSize=14, textColor=colors.white, alignment=TA_RIGHT, fontName='Helvetica-Bold'
            ))]],
            colWidths=[10*cm, page_width - 10*cm]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_header),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (0, 0), 15),
            ('RIGHTPADDING', (1, 0), (1, 0), 15),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 1*cm))

        # 4 Propostas em grid 2x2
        tabelas = self.tabelas_simulacao[:4] if self.tabelas_simulacao else []
        half_width = (page_width - 1*cm) / 2

        def make_proposta(num, tabela=None):
            title_style = ParagraphStyle('PropTitle', fontSize=14, fontName='Helvetica-Bold', alignment=TA_LEFT)
            content_style = ParagraphStyle('PropContent', fontSize=10, fontName='Helvetica', spaceAfter=3)

            if tabela:
                content = [
                    [Paragraph(f"<b>Proposta {num}</b>  (   )", title_style)],
                    [Paragraph(f"Crédito Pretendido: {self._format_currency(tabela.valor_credito)}", content_style)],
                    [Paragraph(f"Entrada Sugerida:", content_style)],
                    [Paragraph(f"Parcelas a partir: {self._format_currency(tabela.parcela)}", content_style)],
                    [Paragraph(f"Prazos Aproximados: {tabela.prazo} meses", content_style)],
                ]
            else:
                content = [
                    [Paragraph(f"<b>Proposta {num}</b>  (   )", title_style)],
                    [Paragraph("Crédito Pretendido:", content_style)],
                    [Paragraph("Entrada Sugerida:", content_style)],
                    [Paragraph("Parcelas a partir:", content_style)],
                    [Paragraph("Prazos Aproximados:", content_style)],
                ]

            t = Table(content, colWidths=[half_width - 0.5*cm])
            t.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            return t

        prop1 = make_proposta('I', tabelas[0] if len(tabelas) > 0 else None)
        prop2 = make_proposta('II', tabelas[1] if len(tabelas) > 1 else None)
        prop3 = make_proposta('III', tabelas[2] if len(tabelas) > 2 else None)
        prop4 = make_proposta('IV', tabelas[3] if len(tabelas) > 3 else None)

        # Linha 1 de propostas
        row1 = Table([[prop1, prop2]], colWidths=[half_width, half_width])
        elements.append(row1)
        elements.append(Spacer(1, 0.5*cm))

        # Linha 2 de propostas
        row2 = Table([[prop3, prop4]], colWidths=[half_width, half_width])
        elements.append(row2)
        elements.append(Spacer(1, 0.5*cm))

        # Observações
        elements.append(Paragraph("<b>OBSERVAÇÕES</b>", ParagraphStyle('ObsTitle', fontSize=12, alignment=TA_CENTER, fontName='Helvetica-Bold')))
        obs_box = Table([['  ']], colWidths=[page_width], rowHeights=[3*cm])
        obs_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(obs_box)
        elements.append(Spacer(1, 0.5*cm))

        # Disclaimer
        disclaimer_style = ParagraphStyle('Disclaimer', fontSize=8, alignment=TA_JUSTIFY, leading=10, fontName='Helvetica')
        elements.append(Paragraph(
            "Declaro ter consciência que à análise de crédito realizada na data de hoje pode resultar na aprovação ou reprovação do crédito com base nas "
            "informações fornecidas na simulação. O cliente reconhece que as condições atuais podem mudar ao longo do tempo devido a alterações em sua "
            "situação pessoal, como renda, profissão, estado civil, entre outros. Também está ciente de que o status de aprovação ou reprovação pode ser "
            "revisado a qualquer momento.",
            disclaimer_style
        ))

        elements.append(Spacer(1, 1*cm))
        self._add_signature_section(elements, with_labels=True)

    def _add_signature_section(self, elements, with_labels=False):
        """Adiciona seção de assinatura"""
        today = datetime.now().strftime("%d/%m/%Y")

        if with_labels:
            sig_data = [
                ['_____________________', today, '_____________________'],
                ['LOCAL', 'DATA', 'ASSINATURA DO CLIENTE'],
            ]
        else:
            sig_data = [
                ['_____________________', today, '_____________________'],
                ['LOCAL', 'DATA', 'Assinatura do cliente'],
            ]

        sig_table = Table(sig_data, colWidths=[5.5*cm, 4*cm, 5.5*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(sig_table)

    def generate(self):
        """Gera o PDF e retorna os bytes"""
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

        # Página 2: Cadastro completo com simulação
        self._create_cadastro_page(elements)

        # Página 3: Termos
        self._create_terms_page(elements)

        # Página 4: Proposta de Orçamento
        self._create_proposal_page(elements)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
