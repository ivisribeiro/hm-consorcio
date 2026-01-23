"""
Serviço de geração de PDF - Contrato de Consultoria e Serviços
Baseado no modelo VENDA.pdf
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime
import locale
import os

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    pass


class ContratoPDFGenerator:
    def __init__(self, cliente, beneficio, usuario=None, empresa=None):
        self.cliente = cliente
        self.beneficio = beneficio
        self.usuario = usuario
        self.empresa = empresa
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()

        # Dados da empresa contratada
        self.empresa_nome = "HM CAPITAL SOLUÇÕES FINANCEIRAS"
        self.empresa_cnpj = "00.000.000/0001-00"
        self.empresa_endereco = "Endereço da Empresa"
        self.empresa_email = "contato@hmcapital.com.br"

        # Cores
        self.cor_header = colors.HexColor('#2E7D32')  # Verde escuro
        self.cor_section = colors.HexColor('#E8F5E9')  # Verde claro

        # Caminho do logo
        self.logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo-white-bg.jpg')

        # Número do contrato
        self.numero_contrato = f"{datetime.now().year}{str(beneficio.id).zfill(6)}"

        # Data atual
        self.data_atual = datetime.now()
        self.data_formatada = self.data_atual.strftime("%d/%m/%Y %H:%M:%S")
        self.data_extenso = self._data_extenso()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='ContractTitle',
            fontSize=11,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=14
        ))

        self.styles.add(ParagraphStyle(
            name='ContractText',
            fontSize=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=11,
            spaceAfter=6
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='ClauseTitle',
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            spaceBefore=8,
            spaceAfter=4
        ))

        self.styles.add(ParagraphStyle(
            name='ClauseText',
            fontSize=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=11,
            spaceAfter=4
        ))

        self.styles.add(ParagraphStyle(
            name='SmallText',
            fontSize=7,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=9
        ))

        self.styles.add(ParagraphStyle(
            name='Footer',
            fontSize=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))

    def _data_extenso(self):
        meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        return f"{self.data_atual.day} de {meses[self.data_atual.month - 1]} de {self.data_atual.year}"

    def _format_cpf(self, cpf):
        if not cpf:
            return ""
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf

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
            return "R$ 0,00"
        try:
            return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return f"R$ {value}"

    def _create_section_header(self, text, width):
        header = Table(
            [[Paragraph(text, self.styles['ClauseTitle'])]],
            colWidths=[width]
        )
        header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cor_header),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return header

    def _add_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(2*cm, 1.5*cm, f"Emitido em: {self.data_formatada}")
        canvas.drawRightString(self.width - 2*cm, 1.5*cm, f"Página {doc.page} de 10")
        canvas.restoreState()

    def _create_page1(self, elements):
        """Página 1 - Dados cadastrais e valores"""
        page_width = self.width - 3*cm

        # Logo no cabeçalho
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=4*cm, height=1.5*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.3*cm))

        # Título do contrato
        title = """CONTRATO DE CONSULTORIA E SERVIÇOS DIGITAIS PARA
ADESÃO A GRUPO DE CONSÓRCIO DE BENS MÓVEIS E
IMÓVEIS, NÃO CONTEMPLADOS"""
        elements.append(Paragraph(title, self.styles['ContractTitle']))
        elements.append(Spacer(1, 0.3*cm))

        # Texto introdutório
        intro = f"""Por este instrumento particular de CONTRATO, de um lado, a empresa {self.empresa_nome}, pessoa jurídica de direito
privado, inscrita no CNPJ sob o nº {self.empresa_cnpj}, com sede em {self.empresa_endereco}, e-mail {self.empresa_email}, neste ato representado por seu representante legal, doravante denominado simplesmente
"CONTRATADA", e, de outro lado, o(a) cliente abaixo identificado(a), doravante denominado(a) simplesmente "CONTRATANTE", têm entre si
justos e contratados o que segue, nos termos e condições abaixo:"""
        elements.append(Paragraph(intro, self.styles['ContractText']))
        elements.append(Spacer(1, 0.3*cm))

        # DADOS CADASTRAIS
        elements.append(self._create_section_header("DADOS CADASTRAIS (OBRIGATÓRIO PREENCHER TODOS OS CAMPOS) - CONTRATANTE", page_width))

        sexo_map = {'masculino': 'MASCULINO', 'feminino': 'FEMININO', 'outro': 'OUTRO'}
        sexo = sexo_map.get(self.cliente.sexo, self.cliente.sexo or '')

        # Número do contrato no canto
        elements.append(Paragraph(f"<b>Nº Contrato: {self.numero_contrato}</b>",
            ParagraphStyle('ContractNum', fontSize=9, alignment=TA_RIGHT, fontName='Helvetica-Bold')))

        cadastro_data = [
            ['Nome/Razão Social do cliente', '', 'Data Nascimento:', 'Sexo:', 'CPF/CNPJ:'],
            [self.cliente.nome or '', '', self._format_date(self.cliente.data_nascimento), sexo, self._format_cpf(self.cliente.cpf)],
            ['RG / IE:', 'Data Expedição:', 'Órgão Exp./UF:', 'Profissão:', 'Nacionalidade:'],
            [self.cliente.identidade or '', self._format_date(self.cliente.data_expedicao), self.cliente.orgao_expedidor or '', self.cliente.cargo or '', self.cliente.nacionalidade or 'BRASILEIRA'],
            ['Nome do cônjuge:', '', 'Data Nasc. cônjuge:', '', 'Naturalidade:'],
            [self.cliente.conjuge_nome or '', '', self._format_date(self.cliente.conjuge_data_nascimento), '', self.cliente.naturalidade or ''],
        ]

        cadastro_table = Table(cadastro_data, colWidths=[4*cm, 3*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        cadastro_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (0, 0), (1, 0)), ('SPAN', (0, 1), (1, 1)),
        ]))
        elements.append(cadastro_table)
        elements.append(Spacer(1, 0.2*cm))

        # Telefone e Email
        tel_data = [
            ['Telefone:', 'Telefone 2:', 'E-MAIL:'],
            [self.cliente.telefone or '', self.cliente.telefone_secundario or '', self.cliente.email or ''],
        ]
        tel_table = Table(tel_data, colWidths=[5.8*cm, 5.8*cm, 5.8*cm])
        tel_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(tel_table)
        elements.append(Spacer(1, 0.2*cm))

        # ENDEREÇO
        elements.append(self._create_section_header("ENDEREÇO RESIDENCIAL / COMERCIAL", page_width))

        endereco_completo = f"{self.cliente.logradouro or ''}, {self.cliente.cep or ''}"

        end_data = [
            ['Rua/Avenida:', '', '', 'N°:'],
            [endereco_completo, '', '', self.cliente.numero or ''],
            ['Bairro:', 'Cidade:', '', 'Estado:'],
            [self.cliente.bairro or '', self.cliente.cidade or '', '', self.cliente.estado or ''],
        ]
        end_table = Table(end_data, colWidths=[6*cm, 5*cm, 3*cm, 3.5*cm])
        end_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (0, 0), (2, 0)), ('SPAN', (0, 1), (2, 1)),
            ('SPAN', (1, 2), (2, 2)), ('SPAN', (1, 3), (2, 3)),
        ]))
        elements.append(end_table)
        elements.append(Spacer(1, 0.2*cm))

        # REPRESENTANTE AUTORIZADO
        elements.append(self._create_section_header("REPRESENTANTE AUTORIZADO", page_width))

        rep_nome = self.usuario.nome if self.usuario else ''
        empresa_nome = self.empresa.nome_fantasia if self.empresa else ''

        rep_data = [
            ['Empresa:', '', 'Preposto:'],
            [empresa_nome, '', rep_nome],
            ['Assinatura:', '', ''],
        ]
        rep_table = Table(rep_data, colWidths=[8.5*cm, 4*cm, 5*cm])
        rep_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (0, 0), (1, 0)), ('SPAN', (0, 1), (1, 1)),
            ('SPAN', (0, 2), (2, 2)),
        ]))
        elements.append(rep_table)
        elements.append(Spacer(1, 0.2*cm))

        # TAXAS E VALORES
        elements.append(self._create_section_header("TAXAS E VALORES APROXIMADOS DO PLANO A SER CONTRATADO NA ADMINISTRADORA DE CONSÓRCIO", page_width))

        tipo_bem_map = {'imovel': 'IMÓVEL', 'carro': 'CARRO', 'moto': 'MOTO'}
        tipo_bem = tipo_bem_map.get(self.beneficio.tipo_bem, self.beneficio.tipo_bem or '')

        # Calcular valor primeira parcela (exemplo: 5% do crédito)
        valor_credito = float(self.beneficio.valor_credito or 0)
        valor_primeira_parcela = valor_credito * 0.05  # Ajustar conforme regra de negócio

        taxas_data = [
            ['Prazo Grupo:', 'Prazo Cota:', 'Valor do Crédito:', 'Valor 1º Parcela:', 'Índice de Correção:'],
            [str(self.beneficio.prazo_grupo or ''), str(self.beneficio.prazo_grupo or ''), self._format_currency(self.beneficio.valor_credito), self._format_currency(valor_primeira_parcela), self.beneficio.indice_correcao or 'INCC'],
            ['Fundo de Reserva:', 'Seguro Prestamista:', 'Tx. Adm. Total:', 'Valor Demais Parcelas:', 'Tipo do Bem:'],
            [f"{self.beneficio.fundo_reserva or 0} %", '0.0 %', f"{self.beneficio.taxa_administracao or 0} %", self._format_currency(self.beneficio.parcela), tipo_bem],
            ['Grupo:', 'Cota:', 'Qtde. Participantes:', 'Tipo Plano:', ''],
            [self.beneficio.grupo or '', self.beneficio.cota or '', '', 'NORMAL', ''],
        ]

        taxas_table = Table(taxas_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        taxas_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('BACKGROUND', (0, 4), (-1, 4), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(taxas_table)
        elements.append(Spacer(1, 0.2*cm))

        # RECIBO
        elements.append(self._create_section_header("RECIBO E FORMA DO PAGAMENTO INICIAL", page_width))

        # Calcular valores
        valor_taxa_servico = valor_primeira_parcela * 0.8  # Exemplo
        valor_parcela_inicial = valor_primeira_parcela * 0.2

        recibo_text1 = f"""Recebemos a importância de {self._format_currency(valor_taxa_servico)} na forma abaixo descrita, sendo este valor referente ao pagamento da taxa de serviço da
HM Capital e prestação de serviços de consultoria, aos quais declara o(a) CONTRATANTE ciente de que não se trata de Cota
contemplada, Financiamento ou Empréstimo."""

        elements.append(Paragraph(recibo_text1, self.styles['ClauseText']))
        elements.append(Paragraph("Assinatura do(a) contratante", self.styles['SmallText']))
        elements.append(Spacer(1, 0.5*cm))

        recibo_text2 = f"""Recebemos a importância de {self._format_currency(valor_parcela_inicial)}, referente a parcela inicial do plano escolhido pela CONTRATANTE. A
CONTRATADA a promover a contratação da cota adequada na administradora de consórcio, efetuar a sua adesão sem reservas e
transferir os valores correspondentes a parcela inicial do plano aderido, no valor de {self._format_currency(self.beneficio.valor_credito)}."""

        elements.append(Paragraph(recibo_text2, self.styles['ClauseText']))
        elements.append(Paragraph("Assinatura do(a) contratante", self.styles['SmallText']))

        # Local
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"{self.cliente.cidade or 'LOCAL'} - {self.cliente.estado or 'UF'}",
            ParagraphStyle('Local', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold')))

        elements.append(PageBreak())

    def _create_page2(self, elements):
        """Página 2 - Conta bancária e cláusulas 1-4"""
        page_width = self.width - 3*cm

        # CONTA BANCÁRIA
        elements.append(self._create_section_header("CONTA BANCÁRIA INDICADA PELO CLIENTE PARA EVENTUAL CONTEMPLAÇÃO/RESTITUIÇÃO DE VALORES", page_width))

        banco_data = [
            ['Banco:', 'Tipo de Conta:', 'Agência:', 'Conta'],
            [self.cliente.banco or '', self.cliente.tipo_conta or '', self.cliente.agencia or '', self.cliente.conta or ''],
            ['Chave Pix Nominal:', '', '', ''],
            [self.cliente.chave_pix or self._format_cpf(self.cliente.cpf), '', '', ''],
        ]

        banco_table = Table(banco_data, colWidths=[4.5*cm, 4.5*cm, 4*cm, 4.5*cm])
        banco_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (0, 2), (3, 2)),
            ('SPAN', (0, 3), (3, 3)),
        ]))
        elements.append(banco_table)
        elements.append(Spacer(1, 0.5*cm))

        # CLÁUSULA 1
        elements.append(self._create_section_header("1. DEFINIÇÃO TERMOS TÉCNICOS", page_width))

        clausula1 = """(i) CONSÓRCIO: reunião de pessoas naturais e jurídicas em grupo, com prazo de duração e número de cotas previamente determinados,
promovida por administradora de consórcio, com a finalidade de propiciar a seus integrantes, de forma isonômica, a aquisição de bens ou
serviços, por meio de autofinanciamento, conforme art. 2º da Lei 11.795/08;

(ii) GRUPO DE CONSÓRCIO: sociedade não personificada constituída por consorciados para os fins estabelecidos no art. 2º da Lei
11.795/2008;

(iii) ADMINISTRADORA DE CONSÓRCIO: pessoa jurídica prestadora de serviços com objeto social principal voltado à administração de
grupos de consórcio, constituída sob a forma de sociedade limitada ou sociedade anônima, nos termos do art. 7º, inciso I da Lei
11.795/2008;

(iv) INTERMEDIADORA/MANDATÁRIA: pessoa jurídica prestadora dos serviços de intermediação e assessoramento como a
CONTRATADA, visando avaliação específica de seu perfil e necessidade para inclusão em um grupo adequado em administradora de
consórcios, devidamente autorizada pelo Banco Central do Brasil (BACEN), com acompanhamento até a contemplação e aquisição do bem
ou serviço pretendido. O objeto da INTERMEDIADORA/MANDATÁRIA se constitui de obrigação de meio e não de resultado."""

        elements.append(Paragraph(clausula1, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 2
        elements.append(self._create_section_header("2. OBJETO", page_width))

        clausula2 = """2.1. O presente CONTRATO tem por objeto a prestação de serviços de intermediação especializados, pela CONTRATADA, na
prospecção/negociação entre o CONTRATANTE e as administradoras de grupos de consórcio, visando o levantamento de perfil,
necessidade e adesão a grupo de consórcio, fornecendo, ainda, suporte até a efetivação de sua contemplação e entrega do bem.

2.1.1. A atuação da CONTRATADA, fica restrita a mediação e/ou intermediação da relação jurídica entre o CONTRATANTE e a
administradora do grupo de consórcio, não se responsabilizando ou se solidarizando sobre o referido negócio. Todas as parcelas e taxas
devidas à Administradora de Consórcio são responsabilidade da CONTRATANTE."""

        elements.append(Paragraph(clausula2, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 3
        elements.append(self._create_section_header("3. MANDATO", page_width))

        clausula3 = """3.1. O(A) CONTRATANTE, para fins de execução deste CONTRATO, confere poderes a empresa CONTRATADA (HM Capital), para
escolha de uma administradora de consórcios, devidamente autorizada pelo poder público, que melhor atenda a seus objetivos. Outorga
amplos poderes de representação perante quaisquer administradoras de consórcios, podendo fazer cotações e levantamentos, assinar
propostas, contratos, adendos, aditivos, enviar documentos, fazer pesquisas cadastrais, prestar declarações e informações para
administradoras com as quais negociar em seu nome, transigir, celebrar contratos, oferecer lances, comparecer em assembleias e nelas
votar.

3.2. O(A) CONTRATANTE autoriza ao HM Capital, às administradoras de consórcios parceiras, de forma direta ou através de seus
prestadores de serviços, a formar banco de dados com suas informações para a execução deste contrato, consultar SRC do Banco Central
do Brasil, SPC, Serasa e similares."""

        elements.append(Paragraph(clausula3, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 4
        elements.append(self._create_section_header("4. OBRIGAÇÕES DA CONTRATADA", page_width))

        clausula4 = """4.1. Aproximar o(a) CONTRATANTE de uma Administradora de consórcio, indicar e alocá-lo(a) em um grupo de consórcio que melhor
atenda o seu perfil, no prazo de 30 (trinta) dias a contar da data da assinatura do presente CONTRATO.

4.1.1. A administradora escolhida, obrigatoriamente, deverá ser autorizada pelo Banco Central do Brasil (BACEN).

4.2. Prestar o atendimento inicial e no transcorrer do grupo, fornecendo suporte ao(a) CONTRATANTE, até a efetivação de sua
contemplação e a entrega do bem.

4.2.1. O atendimento será prestado, exclusivamente, por meio telefônico, e-mail e WhatsApp.

4.2.2. Quando da contemplação da cota, auxiliar no faturamento do bem ou serviço junto à administradora."""

        elements.append(Paragraph(clausula4, self.styles['ClauseText']))

        elements.append(PageBreak())

    def _create_page3(self, elements):
        """Página 3 - Cláusulas 5-9"""
        page_width = self.width - 3*cm

        # CLÁUSULA 5
        elements.append(self._create_section_header("5. OBRIGAÇÕES DA CONTRATANTE", page_width))

        clausula5 = """5.1. Fazer cumprir o negócio jurídico aqui celebrado, com a plena ciência das cláusulas deste CONTRATO e demais anexos que os
acompanham, devidamente assinados.

5.2. Se portar de acordo com a boa-fé, com integridade e confiabilidade para não frustrar a execução deste contrato. Qualquer prejuízo por
informações falsas ou inexatas por parte da CONTRATANTE será de sua exclusiva responsabilidade. Caso a CONTRATADA sofra
prejuízos por informações falsas ou inexatas por parte da CONTRATANTE, esta deverá se responsabilizar.

5.3. Manter sempre atualizado o seu endereço, telefone/WhatsApp e PIX, junto à CONTRATADA, informando, por escrito, todas as
eventuais alterações, sob pena de perda de prazos e frustração da execução deste contrato, os quais sob nenhuma hipótese será
responsabilidade da CONTRATADA.

5.4. Após o seu ingresso ao grupo de consórcio, se obriga a respeitar todas as cláusulas do CONTRATO de adesão e normativos vigentes,
bem como contatar a CONTRATADA, sempre que houver dúvida ou esclarecimentos quanto ao negócio pactuado, bem como ao
funcionamento do consórcio.

5.5. Efetuar o pagamento das parcelas contratadas com absoluta pontualidade.

5.6. Efetuar a assinatura de documentos da contratação, ofertas de lance, faturamento, de acordo com os prazos consignados.

5.7. O(A) CONTRATANTE declara ter condições econômico-financeiras para assumir as obrigações pretendidas por este contrato, perante
o grupo de consórcio, na forma da Resolução BCB nº 285 e 362."""

        elements.append(Paragraph(clausula5, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 6
        elements.append(self._create_section_header("6. SERVIÇOS", page_width))

        clausula6 = """6.1. A CONTRATADA atuará de acordo com as especificações descritas neste instrumento, com ética e responsabilidade. A
CONTRATADA, como mandatária da CONTRATANTE, deverá prestar informações acerca das pesquisas, negociações, aprovações de
cadastros, cláusulas de contratos, condicionantes de cada proposta, contemplação e faturamento de bens.

6.2. O serviço prestado corresponde à intermediação e/ou mediação entre o(a) CONTRATANTE e a administradora do grupo de consórcio
quanto à aquisição de cota de participação, sem que a CONTRATADA realize qualquer ato de administração de cotas de consórcio.

6.2.1. O presente instrumento não se confunde com contrato de adesão a grupo de consórcio, nem com financiamento ou qualquer outra
contratação protegida pelo sistema financeiro, tendo caráter exclusivamente de intermediação e assessoria para a adesão em grupo de
consórcio e prestação dos serviços de orientação, até a contemplação da cota e entrega do bem.

6.3. Não constitui obrigação da CONTRATADA a realização da venda de cota de participação em grupo de consórcios para terceiros."""

        elements.append(Paragraph(clausula6, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 7
        elements.append(self._create_section_header("7. PAGAMENTO", page_width))

        clausula7 = """7.1. O pagamento referente ao item RECIBO se refere à serviços de consultoria da CONTRATADA, que deverá ser efetuado somente
através de boleto bancário, pix ou depósitos feitos diretamente para o HM Capital. Jamais poderão ser efetuados pagamentos para
colaboradores ou supostos cobradores que não seja o próprio HM Capital. O valor referente à parcela do consórcio será repassado à
Administradora após a sua aprovação."""

        elements.append(Paragraph(clausula7, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 8
        elements.append(self._create_section_header("8. PRAZO DO CONTRATO", page_width))

        clausula8 = """8.1. Os direitos e obrigações iniciam a partir do pagamento total a título de taxa de serviço da HM Capital e vigerá até a data da
contemplação e faturamento do bem ou serviços.

8.1.1. Na hipótese de desistência, pelo(a) CONTRATANTE, após a participação em assembleia ordinária de distribuição de bens, no grupo
de consórcio e antes de sua contemplação, o presente instrumento vigerá até a contemplação da cota desistente, sendo obrigação da
CONTRATADA, acompanhar e conferir o cálculo dos valores a serem restituídos ao(a) CONTRATANTE."""

        elements.append(Paragraph(clausula8, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 9
        elements.append(self._create_section_header("9. RESCISÃO E DEVOLUÇÃO", page_width))

        clausula9 = """9.1. O presente CONTRATO é celebrado por prazo determinado, contemplação da cota e entrega do bem ou em caso de desistência do
consórcio, a contemplação da cota por desistência, podendo, com antecedência de 30 (trinta) dias, ser denunciado unilateralmente. A
denúncia deverá ser encaminhada por escrito e com protocolo de recebimento."""

        elements.append(Paragraph(clausula9, self.styles['ClauseText']))

        elements.append(PageBreak())

    def _create_page4(self, elements):
        """Página 4 - Continuação cláusula 9 e cláusulas 10-12"""
        page_width = self.width - 3*cm

        clausula9_cont = """9.1.1. Ocorrendo a rescisão pelo CONTRATANTE, este declara ciente que não terá direito à restituição ao valor pago a título de assessoria,
visto que, além dos serviços prestados até a data da rescisão, a CONTRATADA permanecerá na obrigação do acompanhamento da cota
até a contemplação do(a) CONTRATANTE, junto à administradora de consórcio.

9.1.2. Caso o(a) CONTRATANTE rescinda ou desista da participação no grupo de consórcio, independente do motivo, este declara ciente
que terá direito à restituição apenas dos valores comprovadamente transferidos e já pagos à administradora do grupo de consórcio e
somente receberá quando da contemplação da cota desistente, nos termos dos artigos 22 e 30, da Lei Federal 11.795/08.

9.1.3. Caso a parte denunciante seja a CONTRATADA, a resilição contratual representará a devolução integral do valor pago a título da
assessoria, devidamente corrigido pelo INPC, decotado os valores, comprovadamente, transferidos a administradora de consórcio,
permanecendo o(a) CONTRATANTE com as obrigações decorrentes de sua participação no grupo de consórcio.

9.2. O(A) CONTRATANTE poderá rescindir unilateralmente o presente instrumento, por meio de carta escrita de próprio punho, sem
necessidade de justificativa, no prazo de até 7 (sete) dias, em conformidade com a Lei Federal nº 8.078/90 (Código de Defesa do
Consumidor), com direito à restituição integral do valor de adesão pago, desde que respeitado o disposto na cláusula 9.3.

9.3. Caso a rescisão ocorra após 24 (vinte e quatro) horas da assinatura deste contrato, será aplicada uma multa rescisória de até 20%
(vinte por cento) do valor pago, a título de custos operacionais e administrativos, descontada dos valores a serem restituídos ao (à)
CONTRATANTE.

9.4. Em caso de cancelamento realizado dentro do prazo legal de 7 (sete) dias corridos, o valor pago pelo(à) CONTRATANTE será
restituído no prazo máximo de até 30 (trinta) dias úteis, contados a partir da data da solicitação formal de cancelamento, descontando-se
20% (vinte por cento) do montante total, a título de taxa administrativa da intermediadora, destinada a cobrir os custos operacionais e de
intermediação já realizados."""

        elements.append(Paragraph(clausula9_cont, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 10
        elements.append(self._create_section_header("10. INDEPENDÊNCIA ENTRE AS CLÁUSULAS", page_width))

        clausula10 = """10.1. A não validade, no todo ou em parte, de qualquer disposição deste instrumento, não afetará a validade ou a responsabilidade de
quaisquer das outras cláusulas."""

        elements.append(Paragraph(clausula10, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 11
        elements.append(self._create_section_header("11. CONFIDENCIALIDADE - CLÁUSULA PENAL", page_width))

        clausula11 = """11.1. As partes se obrigam em manter a confidencialidade de toda a relação negocial deste instrumento e convencionam a título de cláusula
penal o pagamento, a quem der causa, de multa pecuniária correspondente ao valor de 10 (dez) vezes ao pagamento total inicial (item 3),
devidamente atualizado pelo INCC, à época do descumprimento."""

        elements.append(Paragraph(clausula11, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 12
        elements.append(self._create_section_header("12. DISPOSIÇÕES GERAIS", page_width))

        clausula12 = """12.1. Este CONTRATO e as cláusulas que o compõem não poderão se emendados, cancelados, abandonados ou alterados em qualquer
forma, exceto através de acordo mútuo, firmado pelas partes.

12.2. Este CONTRATO, uma vez firmado pelas partes, constituirá compromisso irretratável, irrevogável, incondicional e o acordo completo e
final entre as partes, substituindo todos os pré-entendimentos, compromissos, cartas, mensagens enviadas pelo aplicativo WhatsApp, e-mails ou correspondências anteriores e em relação à negociação, que mediante este contrato foi firmado e aperfeiçoado.

12.3. Cada cláusula, parágrafo, frase ou sentença deste CONTRATO constitui um compromisso ou disposição independente e distinta.
Sempre que possível, cada cláusula deste CONTRATO deverá ser interpretada de modo a se tornar válida e eficaz à luz da lei aplicável.

12.4. A tolerância, por qualquer das partes, com relação ao descumprimento de qualquer termo ou condição aqui ajustado, não será
considerada como desistência em exigir o cumprimento de disposição nele contida.

12.5. Sobrevindo a ocorrência de casos fortuitos ou força maior que impossibilitem a execução dos serviços e que independam da vontade
da CONTRATADA, o CONTRATO poderá ser suspenso até que cesse o referido motivo ou encerrado em comum acordo.

12.6. É defeso a qualquer das partes ceder ou transferir total ou parcial direitos e obrigações decorrentes deste CONTRATO, sem
autorização expressa e por escrito de ambas as partes.

12.7. O(A) CONTRATANTE reconhece a inexistência e a exclusão de qualquer espécie de responsabilidade por parte da CONTRATADA,
referente a todo e qualquer prejuízo, perda, passivo, custo, demanda, que estejam relacionados ao CONTRATO de participação em grupo
de consórcios, junto a administradora de consórcios, escolhida e ratificada pelo(a) CONTRATANTE.

12.8. O(A) CONTRATANTE autoriza expressamente a coleta, tratamento e manutenção de seus dados pela CONTRATADA para a
execução deste contrato."""

        elements.append(Paragraph(clausula12, self.styles['ClauseText']))

        elements.append(PageBreak())

    def _create_page5(self, elements):
        """Página 5 - Cláusulas 13-14, assinaturas e PEP"""
        page_width = self.width - 3*cm

        # CLÁUSULA 13
        elements.append(self._create_section_header("13. DECLARAÇÕES E DO CONHECIMENTO PRÉVIO", page_width))

        clausula13 = """13.1. O(A) CONTRATANTE, neste ato, declara saber que:

(i) nenhuma promessa ou proposta extracontratual e extra normativos do sistema de consórcios lhe foi feita. Informa que leu atentamente
todas as cláusulas e condições do presente instrumento, obtendo assim, todas as informações necessárias para o perfeito conhecimento
das regras de funcionamento do produto consórcio e que autoriza sua contabilização definitiva na empresa escolhida, sem nenhuma
restrição;

(ii) ALERTA AO CONSUMIDOR: Nenhum documento, promessa escrita, verbal ou gravada, feitas ou firmadas por terceiros, ou mesmo por
funcionários sem poderes de gestão, que não sejam os representantes legais da CONTRATADA, não terão nenhuma validade,
prevalecendo somente as cláusulas contratuais;

(iii) que autoriza a CONTRATADA a consultar quaisquer informações disponibilizadas pelos órgãos de proteção ao crédito.

(iv) Em caso de desistência por parte da CONTRATANTE, os valores pagos a título de intermediação e assessoria não poderão ser
devolvidos por se tratar de serviço já prestado."""

        elements.append(Paragraph(clausula13, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # CLÁUSULA 14
        elements.append(self._create_section_header("14. FORO", page_width))

        clausula14 = """14.1. Para dirimir quaisquer questões oriundas do presente CONTRATO, as partes elegem o foro da Comarca de São Paulo, Estado de São
Paulo, com renúncia expressa de qualquer outro, por mais privilegiado que seja ou venha a ser."""

        elements.append(Paragraph(clausula14, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.5*cm))

        # Data e assinaturas
        elements.append(Paragraph(f"SÃO PAULO-SP, {self.data_extenso}.",
            ParagraphStyle('DataLocal', fontSize=9, alignment=TA_CENTER)))
        elements.append(Spacer(1, 0.5*cm))

        sig_data = [
            ['Assinatura da CONTRATADA', '', 'Assinatura do(a) CONTRATANTE'],
            ['', '', ''],
        ]
        sig_table = Table(sig_data, colWidths=[7*cm, 3.5*cm, 7*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
            ('LINEBELOW', (2, 1), (2, 1), 1, colors.black),
        ]))
        elements.append(sig_table)
        elements.append(Spacer(1, 0.3*cm))

        # Testemunhas
        elements.append(Paragraph("<b>TESTEMUNHAS</b>", ParagraphStyle('Test', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold')))
        test_data = [['', '', ''], ['', '', '']]
        test_table = Table(test_data, colWidths=[5.8*cm, 5.8*cm, 5.8*cm])
        test_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(test_table)
        elements.append(Spacer(1, 0.3*cm))

        # PEP
        elements.append(self._create_section_header("DECLARAÇÃO DE PESSOA POLITICAMENTE EXPOSTA-PEP", page_width))

        pep_text = """O objetivo desta declaração é atender as diretrizes do Banco Central do Brasil Bacen e do COAF/UIF que administradoras de consórcio
devem adotar, para controles e acompanhamento dos negócios e movimentações financeiras das pessoas politicamente expostas a fim de
atender dispostos na lei 9.613 de 3 de Março de 1998.

São considerados pessoas politicamente expostas todas aquelas que previstas no artigo 4º da circular do Banco Central do Brasil BACEN
de nº 3.461 de 24 de julho de 2009 da qual consorciado abaixo-assinado declara ter conhecimento.

• Sou pessoa politicamente exposta __________.
• Possuo parentes de primeiro grau pais ou filhos cônjuges companheiro, enteado inclusive representante pessoas que possam ter minha
procuração que possam ser considerados pessoas politicamente expostas __________.
• Estou enquadrado como Estreito colaborador de pessoa politicamente exposta como definido pelo COAF __________.

Declaro sob as penas da lei que as informações aqui prestadas são expressão da Verdade pelas quais me responsabilizo com a
veracidade e exatidão das informações prestadas."""

        elements.append(Paragraph(pep_text, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        # Assinatura PEP
        pep_sig = [
            ['Nome', 'CPF', 'RG'],
            [self.cliente.nome or '', self._format_cpf(self.cliente.cpf), self.cliente.identidade or ''],
            ['Local/Data', 'Assinatura do consorciado / Conforme documento', ''],
            [f"SÃO PAULO-SP, {self.data_extenso}.", '', ''],
        ]
        pep_table = Table(pep_sig, colWidths=[7*cm, 5*cm, 5.5*cm])
        pep_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (1, 2), (2, 2)),
            ('SPAN', (1, 3), (2, 3)),
        ]))
        elements.append(pep_table)

        elements.append(PageBreak())

    def _create_page6(self, elements):
        """Página 6 - Declaração de Ciência"""
        page_width = self.width - 3*cm

        elements.append(self._create_section_header("DECLARAÇÃO DE CIÊNCIA", page_width))
        elements.append(Spacer(1, 0.3*cm))

        ciencia_text = f"""Declaro para os devidos fins de Direito que ao contratar os serviços:

Tomou ciência na data de hoje, que do valor pago nessa ocasião da contratação será passado o valor aproximado de {self._format_currency(self.beneficio.parcela)} para a
administradora de consórcios, a ser contratada a título de primeira parcela do consórcio, e o saldo remanescente será utilizado para
pagamentos de custas de contratação da intermediação tais como custas comerciais, e administrativas conforme contrato de intermediação
na adesão a grupo de consórcio não contemplados. Desde já fica autorizado tais repasses descritos aqui, através dessa declaração e
ratificação através do instrumento particular de contratação, aditivos e checagem telefônica gravada."""

        elements.append(Paragraph(ciencia_text, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.5*cm))

        # Assinatura
        sig_data = [
            ['Nome', 'CPF', 'RG'],
            [self.cliente.nome or '', self._format_cpf(self.cliente.cpf), self.cliente.identidade or ''],
            ['Local/Data', 'Assinatura do consorciado / Conforme documento', ''],
            [f"SÃO PAULO-SP, {self.data_extenso}.", '', ''],
        ]
        sig_table = Table(sig_data, colWidths=[7*cm, 5*cm, 5.5*cm])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (1, 2), (2, 2)),
            ('SPAN', (1, 3), (2, 3)),
        ]))
        elements.append(sig_table)

        elements.append(PageBreak())

    def _create_page7(self, elements):
        """Página 7 - Termo de Contratação 1"""
        page_width = self.width - 3*cm

        elements.append(self._create_section_header("TERMO DE CONTRATAÇÃO DE SERVIÇOS DE CONSULTORIA FINANCEIRA", page_width))
        elements.append(Spacer(1, 0.3*cm))

        termo_text = """A HM Capital atua exclusivamente na consultoria financeira para aquisição de consórcios não contemplados, facilitando a conexão entre
o cliente e a administradora de consórcios. Essa consultoria é realizada por meio de seus consultores credenciados, que são pessoas
jurídicas autônomas e possuem liberdade para cobrar pelos serviços de atendimento e vendas prestadas.

O(a) PROPONENTE declara, conforme a lei, que preencheu uma proposta de consultoria financeira com a HM Capital para adquirir um
consórcio não contemplado e está ciente de que deve aguardar a contemplação por meio de sorteio pela Loteria Federal ou lance,
conforme o regulamento geral de consórcios.

O(a) PROPONENTE está ciente de que sua proposta será comprovada pelo setor de qualidade da HM Capital e, somente após
validação, seu contrato será apresentado à administradora e incluído no grupo de consórcio.

O(a) PROPONENTE declara ter lido e compreendido todas as cláusulas do regulamento do consórcio, em conformidade com a Lei nº
11.795/2008, incluindo suas obrigações, taxas e formas de contemplação, e que não restam dúvidas sobre a negociação assumida.

O(a) PROPONENTE autoriza que a contratação de uma consultoria financeira para consórcio não é obrigatória, mas aceita livremente os
termos e condições contratuais propostas.

O(a) PROPONENTE também declara estar ciente de que os valores pagos na adesão referem-se à inclusão no grupo de consórcio, à taxa
administrativa da administradora e à taxa de consultoria pela prestação de serviços da HM Capital."""

        elements.append(Paragraph(termo_text, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.5*cm))

        # Assinatura
        sig_data = [
            ['Nome', 'CPF', 'RG'],
            [self.cliente.nome or '', self._format_cpf(self.cliente.cpf), self.cliente.identidade or ''],
            ['Local/Data', 'Assinatura do consorciado / Conforme documento', ''],
            [f"SÃO PAULO-SP, {self.data_extenso}.", '', ''],
        ]
        sig_table = Table(sig_data, colWidths=[7*cm, 5*cm, 5.5*cm])
        sig_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section),
            ('BACKGROUND', (0, 2), (-1, 2), self.cor_section),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (1, 2), (2, 2)),
            ('SPAN', (1, 3), (2, 3)),
        ]))
        elements.append(sig_table)

        elements.append(PageBreak())

    def _create_page8(self, elements):
        """Página 8 - Termo de Contratação 2"""
        page_width = self.width - 3*cm

        elements.append(self._create_section_header("TERMO DE CONTRATAÇÃO DE SERVIÇOS DE CONSULTORIA FINANCEIRA", page_width))
        elements.append(Spacer(1, 0.3*cm))

        termo_text2 = """A HM Capital atua como consultora financeira, promovendo a assessoria na aquisição de consórcios não contemplados entre o(a)
CONTRATANTE e a Administradora de Consórcios, por meio de seus consultores financeiros devidamente credenciados, que possuem
independência para realizar a cobrança pelos serviços prestados de atendimento e vendas.

O(a) PROPONENTE declara, sob as penas da lei, que preencheu uma proposta de consultoria financeira junto à HM Capital com o
objetivo de adquirir uma cota de consórcio não contemplada. O(a) PROPONENTE compreende que a contemplação ocorrerá em
conformidade com os termos do regulamento geral da Administradora, seja por sorteio automático ou por lance, e se obrigará a efetuar o
pagamento das parcelas rigorosamente em dia.

O(a) PROPONENTE está ciente de que uma proposta será comprovada pela Administradora de Consórcios e pela HM Capital, que
poderá recusar o caso não atender às exigências legais e às políticas internas da Administradora.

O(a) PROPONENTE declara estar ciente de que o cancelamento do consórcio após a facilidade da proposta poderá gerar prejuízos
financeiros à HM Capital e aos consultores responsáveis pela intermediação, comprometendo-se a reparar eventuais perdas e danos,
incluindo a garantia da comissão de corretagem para o consultor envolvido na revenda da cota.

O(a) PROPONENTE confirma ter lido e compreende todas as cláusulas do regulamento do consórcio, bem como as obrigações e direitos
relacionados à contratação, não restando dúvidas sobre a negociação assumida, conforme previsto na Lei nº 11.795/2008.

O(a) PROPONENTE autoriza que a contratação de uma consultoria financeira não é obrigatória para a aquisição de consórcio, mas aceita
voluntariamente os termos e condições contratuais ou pactuados.

O(a) PROPONENTE concorda que, dos valores pagos na taxa de adesão, a comissão de corretagem será repassada aos consultores de
consórcios, autorizando desde já o pagamento sem que isso gere qualquer prejuízo à HM Capital."""

        elements.append(Paragraph(termo_text2, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        elements.append(Paragraph("<b>LEIA COM ATENÇÃO ANTES DE ASSINAR.</b>",
            ParagraphStyle('Alerta', fontSize=10, alignment=TA_CENTER, textColor=colors.red, fontName='Helvetica-Bold')))
        elements.append(Spacer(1, 0.3*cm))

        elements.append(Paragraph(f"SÃO PAULO-SP, {self.data_extenso}.",
            ParagraphStyle('DataLocal', fontSize=9, alignment=TA_CENTER)))
        elements.append(Spacer(1, 0.2*cm))

        elements.append(Paragraph("<b>NÃO COMERCIALIZAMOS COTAS CONTEMPLADAS.</b>",
            ParagraphStyle('Alerta2', fontSize=10, alignment=TA_CENTER, textColor=colors.red, fontName='Helvetica-Bold')))
        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas
        rep_nome = self.usuario.nome if self.usuario else ''

        final_sig = [
            ['Nome legível do Vendedor', ''],
            [rep_nome, ''],
            ['Nome do cliente + CPF do cliente', ''],
            [f"{self.cliente.nome} - {self._format_cpf(self.cliente.cpf)}", ''],
        ]
        final_table = Table(final_sig, colWidths=[8.5*cm, 8.5*cm])
        final_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
            ('LINEBELOW', (0, 3), (0, 3), 1, colors.black),
        ]))
        elements.append(final_table)

        elements.append(PageBreak())

    def _create_page9(self, elements):
        """Página 9 - Questionário"""
        page_width = self.width - 3*cm

        elements.append(self._create_section_header("TERMO DE CONTRATAÇÃO DE SERVIÇOS DE CONSULTORIA FINANCEIRA", page_width))
        elements.append(Spacer(1, 0.3*cm))

        intro = """Parabéns pela aquisição da sua cota de consórcio é um prazer tê-lo como cliente!

Esperamos poder contar com a sua colaboração para que possamos proceder corretamente com o seu cadastro de contrato, e ao mesmo
tempo realizar uma avaliação da qualidade do serviço prestado pelo nosso consultor de vendas. Para que isso ocorra pedimos que
responda o questionário abaixo com sim ou não:"""

        elements.append(Paragraph(intro, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.3*cm))

        perguntas = f"""Você contratou um serviço de Consultoria com a HM Capital para participar de um consórcio não contemplado? __________

Você confirma que possui capacidade financeira para arcar com as prestações do seu consórcio? __________

Você está ciente que o valor da sua parcela mensal é de {self._format_currency(self.beneficio.parcela)} __________

Tomou ciência que a empresa HM Capital não administra consórcios, apenas promove a consultoria? __________

Você tem ciência que o consórcio não está contemplado? __________

Foi informado(a) de que a contemplação ocorrerá somente por sorteio ou lance fixo ou lance Livre? __________

Lhe foi feita alguma promessa de contemplação, garantia de contemplação em determinado prazo, mediante determinado valor de lance ou
vantagens extras? __________

Ocorrendo a rescisão pelo CONTRATANTE, este declara ciente que não terá direito à restituição ao valor pago a título de assessoria, visto
que, além dos serviços prestados até a data da rescisão, a CONTRATADA permanecerá na obrigação do acompanhamento da cota até a
contemplação do(a) CONTRATANTE, junto a administradora de consórcio. __________

Você leu com atenção todo o contrato de intermediação para adesão a grupo de consórcio e assinou concordando com as cláusulas e
condições somente depois da leitura? __________

Você escolheu participar de um consórcio intermediado pela HM Capital e administrado por Administradoras de Consórcios autorizadas e
fiscalizadas pelo Banco Central? __________

Promovemos a intermediação entre o interessado em consórcio e a administradora legalmente autorizadas pelo Banco Central, através de
seus corretores pessoa Jurídica autônomos credenciados.

Prezado cliente, os seus dados serão inseridos no sistema da administradora e você receberá no seu e-mail o regulamento do consórcio
adquirido. Você receberá também, seu grupo e a cota."""

        elements.append(Paragraph(perguntas, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas
        rep_nome = self.usuario.nome if self.usuario else ''

        final_sig = [
            ['Nome legível do Vendedor', ''],
            [rep_nome, ''],
            ['Nome do cliente + CPF do cliente', ''],
            [f"{self.cliente.nome} - {self._format_cpf(self.cliente.cpf)}", ''],
        ]
        final_table = Table(final_sig, colWidths=[8.5*cm, 8.5*cm])
        final_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
            ('LINEBELOW', (0, 3), (0, 3), 1, colors.black),
        ]))
        elements.append(final_table)

        elements.append(PageBreak())

    def _create_page10(self, elements):
        """Página 10 - Ciência Análise Creditícia"""
        page_width = self.width - 3*cm

        elements.append(self._create_section_header("CIÊNCIA E CONCORDÂNCIA COM A ANÁLISE CREDITÍCIA PRÉVIA À AQUISIÇÃO DE COTA DE CONSÓRCIO", page_width))
        elements.append(Spacer(1, 0.3*cm))

        ciencia_text = """1. Estou ciente de que, após realização de uma simulação na data de assinatura deste, com base em consultas aos órgãos de proteção ao
crédito, na renda por mim informada e nos documentos por mim apresentados, fui devidamente informado quanto à aprovação ou
reprovação do crédito, no cenário ATUAL, se hoje houvesse a contemplação de cota, seja por sorteio, seja por lance;

2. Estou ciente, ainda, de que o cenário ATUAL está sujeito a mudanças, podendo variar diária, semanal ou mensalmente, conforme as
minhas condições pessoais também se alterem (profissão, renda, estado civil, restrições etc.);

3. Desta forma, estou ciente e de acordo que o status de aprovação ou reprovação pode sofrer alteração a qualquer tempo conforme
minhas condições pessoais também se alterem, sendo que nova análise poderá ser realizada no momento da contemplação;

4. Por fim, declaro que fui informado sobre a análise creditícia e assinei o presente contrato antes de efetivar a minha adesão a qualquer
grupo de consórcio. Declaro que foi ofertado respeitando as leis vigentes em observância ao Código de Defesa do Consumidor e Lei
11.795/2008, deixando claro que a decisão de dar continuidade na compra foi minha, ciente dos prazos e regulamentos atuais.

Declaro expressamente de estar ciente que em decorrência da minha incapacidade financeira junto às instituições de crédito, as quais
indeferiram a aquisição mediante financiamento do bem, autorizo a contratada a proceder com a aquisição do bem por meio de aquisição de
cotas de participação em grupo de consórcio, nos termos elencados no contrato que me foi fornecido e cientificado das cláusulas com a
devida antecedência."""

        elements.append(Paragraph(ciencia_text, self.styles['ClauseText']))
        elements.append(Spacer(1, 0.5*cm))

        elements.append(Paragraph("<b>LEIA COM ATENÇÃO ANTES DE ASSINAR.</b>",
            ParagraphStyle('Alerta', fontSize=10, alignment=TA_CENTER, textColor=colors.red, fontName='Helvetica-Bold')))
        elements.append(Spacer(1, 0.3*cm))

        elements.append(Paragraph(f"SÃO PAULO-SP, {self.data_extenso}.",
            ParagraphStyle('DataLocal', fontSize=9, alignment=TA_CENTER)))
        elements.append(Spacer(1, 0.2*cm))

        elements.append(Paragraph("<b>NÃO COMERCIALIZAMOS COTAS CONTEMPLADAS.</b>",
            ParagraphStyle('Alerta2', fontSize=10, alignment=TA_CENTER, textColor=colors.red, fontName='Helvetica-Bold')))
        elements.append(Spacer(1, 0.5*cm))

        # Assinaturas finais
        rep_nome = self.usuario.nome if self.usuario else ''

        final_sig = [
            ['Nome legível do Vendedor', ''],
            [rep_nome, ''],
            ['Nome do cliente + CPF do cliente', ''],
            [f"{self.cliente.nome} - {self._format_cpf(self.cliente.cpf)}", ''],
        ]
        final_table = Table(final_sig, colWidths=[8.5*cm, 8.5*cm])
        final_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
            ('LINEBELOW', (0, 3), (0, 3), 1, colors.black),
        ]))
        elements.append(final_table)

    def generate(self):
        """Gera o PDF do contrato e retorna os bytes"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=2*cm
        )

        elements = []

        # Gerar todas as páginas
        self._create_page1(elements)
        self._create_page2(elements)
        self._create_page3(elements)
        self._create_page4(elements)
        self._create_page5(elements)
        self._create_page6(elements)
        self._create_page7(elements)
        self._create_page8(elements)
        self._create_page9(elements)
        self._create_page10(elements)

        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        buffer.seek(0)
        return buffer.getvalue()
