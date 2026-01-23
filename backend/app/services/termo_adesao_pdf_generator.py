"""
Serviço de geração de PDF - Termo de Adesão
Baseado no modelo Unifin - 3 páginas
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os


class TermoAdesaoPDFGenerator:
    def __init__(self, cliente, beneficio, usuario=None, empresa=None):
        self.cliente = cliente
        self.beneficio = beneficio
        self.usuario = usuario
        self.empresa = empresa
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()

        # Dados da empresa
        self.empresa_nome = "HM CAPITAL"
        self.empresa_cnpj = empresa.cnpj if empresa and empresa.cnpj else "00.000.000/0001-00"
        self.empresa_endereco = empresa.endereco if empresa and hasattr(empresa, 'endereco') else "São Paulo - SP"

        # Cores
        self.cor_header = colors.HexColor('#1a1a1a')
        self.cor_section_bg = colors.HexColor('#f5f5f5')

        # Caminho do logo
        self.logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo-white-bg.jpg')

        # Data atual
        self.data_atual = datetime.now()
        self.data_formatada = self.data_atual.strftime("%d/%m/%Y")

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='TermoDocTitle',
            fontSize=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=14,
            spaceAfter=10
        ))

        self.styles.add(ParagraphStyle(
            name='TermoCompanyHeader',
            fontSize=11,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=13
        ))

        self.styles.add(ParagraphStyle(
            name='TermoCompanySubHeader',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=11
        ))

        self.styles.add(ParagraphStyle(
            name='TermoSectionTitle',
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='TermoBodyText',
            fontSize=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=11,
            spaceAfter=4
        ))

        self.styles.add(ParagraphStyle(
            name='TermoSmallText',
            fontSize=7,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=9,
            spaceAfter=3
        ))

        self.styles.add(ParagraphStyle(
            name='TermoFooter',
            fontSize=8,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='TermoWarning',
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.red,
            spaceBefore=10
        ))

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

    def _create_header(self, elements):
        """Cabeçalho do documento"""
        # Logo
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=4*cm, height=1.5*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.2*cm))
        else:
            # Nome da empresa (fallback se não houver logo)
            elements.append(Paragraph(self.empresa_nome, self.styles['TermoCompanyHeader']))

        elements.append(Paragraph(self.empresa_endereco, self.styles['TermoCompanySubHeader']))
        elements.append(Paragraph(f"CNPJ: {self.empresa_cnpj}", self.styles['TermoCompanySubHeader']))
        elements.append(Spacer(1, 0.3*cm))

        # Título
        title = "TERMO DE INTERMEDIAÇÃO E CONSULTORIA DE INCLUSÃO AO CLIENTE NO GRUPO DE CONSÓRCIO"
        elements.append(Paragraph(title, self.styles['TermoDocTitle']))
        elements.append(Spacer(1, 0.3*cm))

    def _add_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredString(self.width / 2, 1.5*cm, "1ª Via Cliente - 2ª Via Banco")
        canvas.restoreState()

    def _create_page1(self, elements):
        """Página 1 - Dados cadastrais e características do grupo"""
        page_width = self.width - 3*cm

        self._create_header(elements)

        # DADOS CADASTRAIS DO CONSORCIADO - PF
        elements.append(Paragraph("<b>DADOS CADASTRAIS DO CONSORCIADO - PF</b>", self.styles['TermoSectionTitle']))

        sexo_map = {'masculino': 'Masculino', 'feminino': 'Feminino', 'outro': 'Outro'}
        sexo = sexo_map.get(self.cliente.sexo, self.cliente.sexo or '')

        estado_civil_map = {'solteiro': 'Solteiro', 'casado': 'Casado', 'divorciado': 'Divorciado', 'viuvo': 'Viúvo', 'uniao_estavel': 'União Estável'}
        estado_civil = estado_civil_map.get(self.cliente.estado_civil, self.cliente.estado_civil or '')

        # Tabela de dados cadastrais
        dados = [
            [f"NOME: {self.cliente.nome or ''}", f"SEXO: {sexo}", f"DATA DE NASC.:\n{self._format_date(self.cliente.data_nascimento)}", f"ESTADO CIVIL:\n{estado_civil}"],
            [f"NACIONALIDADE: {self.cliente.nacionalidade or 'Brasil'}", f"NOME DA MÃE: {self.cliente.nome_mae or ''}", "", f"N° DEPENDENTES:\n{getattr(self.cliente, 'numero_dependentes', '') or ''}"],
            [f"TIPO DOCUMENTO: RG ({self.cliente.identidade or ''})", f"DATA EMISSÃO:\n{self._format_date(self.cliente.data_expedicao)}", f"ORGÃO EXP.: {self.cliente.orgao_expedidor or ''}", f"CPF: {self._format_cpf(self.cliente.cpf)}"],
        ]

        t = Table(dados, colWidths=[5*cm, 5*cm, 3.5*cm, 4*cm])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

        # Endereço
        endereco = f"{self.cliente.logradouro or ''}, {self.cliente.numero or ''}, {self.cliente.bairro or ''}, {self.cliente.cidade or ''} - {self.cliente.estado or ''}, {self.cliente.cep or ''}"
        end_data = [[f"ENDEREÇO: {endereco}"]]
        t_end = Table(end_data, colWidths=[page_width])
        t_end.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_end)

        # Telefones
        tel_data = [
            ["TELEFONE RESIDENCIAL:", "TELEFONE COMERCIAL:", f"CELULAR: {self.cliente.telefone or ''}"],
        ]
        t_tel = Table(tel_data, colWidths=[5.8*cm, 5.8*cm, 5.8*cm])
        t_tel.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_tel)

        # Email e cônjuge
        email_data = [
            [f"E-MAIL: {self.cliente.email or ''}", f"CÔNJUGE: {self.cliente.conjuge_nome or ''}"],
        ]
        t_email = Table(email_data, colWidths=[8.7*cm, 8.7*cm])
        t_email.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_email)

        # Profissão, empresa, renda
        renda = self._format_currency(self.cliente.salario) if self.cliente.salario else ""
        prof_data = [
            [f"PROFISSÃO: {self.cliente.cargo or ''}", f"EMPRESA: {self.cliente.empresa_trabalho or ''}", f"RENDA: {renda}"],
        ]
        t_prof = Table(prof_data, colWidths=[5.8*cm, 5.8*cm, 5.8*cm])
        t_prof.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_prof)

        # Patrimônio
        pat_data = [
            ["PATRIMÔNIO:", "IMÓVEL ( )", "VEÍCULOS ( )", "INVESTIMENTOS:"],
        ]
        t_pat = Table(pat_data, colWidths=[4.3*cm, 4.3*cm, 4.3*cm, 4.5*cm])
        t_pat.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_pat)

        # REPRESENTANTE LEGAL
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph("<b>REPRESENTANTE LEGAL</b>", self.styles['TermoSectionTitle']))

        rep_nome = self.usuario.nome if self.usuario else ''
        rep_data = [
            [f"NOME: {rep_nome}", f"CPF:"],
        ]
        t_rep = Table(rep_data, colWidths=[8.7*cm, 8.7*cm])
        t_rep.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_rep)

        # CARACTERÍSTICAS DO GRUPO / COTA
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph("<b>CARACTERÍSTICAS DO GRUPO / COTA</b>", self.styles['TermoSectionTitle']))

        carac_data = [
            [f"VALOR DO CRÉDITO NA DATA DA ADMISSÃO: {self._format_currency(self.beneficio.valor_credito)}", f"PRAZO DE DURAÇÃO: ({self.beneficio.prazo_grupo or ''}) MESES -"],
            [f"NÚMERO MÁXIMO DE PARTICIPANTES: {self.beneficio.qtd_participantes or '9.999'}", ""],
        ]
        t_carac = Table(carac_data, colWidths=[8.7*cm, 8.7*cm])
        t_carac.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_carac)

        # PERCENTUAIS DE TAXAS
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph("<b>PERCENTUAIS DE TAXAS E CONTRIBUIÇÕES MENSAIS</b>", self.styles['TermoSectionTitle']))

        taxa_adm = f"{self.beneficio.taxa_administracao or 0}%"
        fundo_reserva = f"{self.beneficio.fundo_reserva or 0}%"
        indice = self.beneficio.indice_correcao or 'INCC'

        indice_incc = "(X) INCC" if indice == 'INCC' else "( ) INCC"
        indice_ipca = "(X) IPCA" if indice == 'IPCA' else "( ) IPCA"

        taxas_data = [
            [f"TAXA DE ADMINISTRAÇÃO TOTAL: {taxa_adm}", f"FUNDO DE RESERVA: {fundo_reserva}"],
            [indice_incc, indice_ipca, "( ) OUTROS", f"SEGURO DE VIDA MENSAL: {self.beneficio.seguro_prestamista or 0}%"],
        ]
        t_taxas = Table(taxas_data, colWidths=[8.7*cm, 4.3*cm, 2.2*cm, 2.2*cm])
        t_taxas.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('SPAN', (0, 0), (0, 0)),
            ('SPAN', (1, 0), (3, 0)),
        ]))
        elements.append(t_taxas)

        # Texto sobre art. 5
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(
            "EM CONFORMIDADE COM ART. 5° DO REGULAMENTO DE CONSÓRCIO, SERÁ COBRADO DA TAXA DE ADMINISTRAÇÃO TOTAL:",
            self.styles['TermoSmallText']
        ))

        # Tabela de faixas
        valor_parcela = float(self.beneficio.parcela or 0)
        faixas_data = [
            ["Faixa:", "Fundo Comum:", "% Administração:", "% Reserva:", "% Seguro:", "Valor:"],
            ["Parcela 1", "0,111%", "0,333%", "0,000%", "0,000%", self._format_currency(valor_parcela * 0.5)],
            ["Parcela 2 a parcela 12", "0,224%", "0,671%", "0,000%", "0,000%", self._format_currency(valor_parcela)],
            ["Parcela 13 a parcela 66", "0,862%", "0,005%", "0,027%", "0,000%", self._format_currency(valor_parcela)],
            [f"Parcela {self.beneficio.prazo_grupo or 67}", "0,864%", "0,006%", "0,030%", "0,000%", self._format_currency(valor_parcela)],
        ]
        t_faixas = Table(faixas_data, colWidths=[3.5*cm, 2.5*cm, 3*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        t_faixas.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), self.cor_section_bg),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(t_faixas)

        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph(
            f"EM CONFORMIDADE COM OS REGULAMENTO INTERNO DO {self.empresa_nome}, O CLIENTE TEM ACESSO TOTAL AO DESTINO DOS VALORES PAGOS.",
            self.styles['TermoSmallText']
        ))

        # Declarações e Autorizações
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("<b>Declarações e Autorizações</b>", self.styles['TermoSectionTitle']))

        elements.append(Paragraph(
            "O CONSORCIADO, sob as penas da lei e de anulação deste contrato, DECLARA que:",
            self.styles['TermoBodyText']
        ))

        elements.append(Paragraph(
            "1. Tem capacidade financeira para assumir as obrigações perante o grupo de consórcio e a Administradora, em atendimento às circulares 3432 e 3785 do Banco Central do Brasil.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"2. Tem ciência de que o {self.empresa_nome} poderá cobrar taxa de administração diferenciada, entre os participantes deste grupo de consórcio, bem como poderá comercializar créditos de valores diferenciados, em conformidade com a circular 3618 do Banco Central do Brasil.",
            self.styles['TermoSmallText']
        ))

        elements.append(PageBreak())

    def _create_page2(self, elements):
        """Página 2 - Continuação das declarações"""
        self._create_header(elements)

        elements.append(Paragraph(
            f"3. Autoriza o depósito dos recursos sobressalentes no encerramento do grupo. Tipo de conta: ( ) Corrente ( ) Poupança",
            self.styles['TermoSmallText']
        ))

        banco_info = f"Banco: {self.cliente.banco or '_________'} Agência: {self.cliente.agencia or '_________'} Conta: {self.cliente.conta or '_________'} | Chave PIX: {self.cliente.chave_pix or '_____________________'}"
        elements.append(Paragraph(banco_info, self.styles['TermoSmallText']))

        elements.append(Paragraph(
            f"4. Autoriza ao {self.empresa_nome} e as administradoras parceiras de forma direta ou através de suas coligadas ou prestadores a consultar suas informações cadastrais na Central de Risco do Banco Central do Brasil, nas instituições financeiras, cadastros mantidos pelo SPC/Serasa e entidades congêneres.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"5. Autoriza os gestores de banco de dados de que trata a Lei nº 12.414, de 9 de junho de 2011, a disponibilizar ao {self.empresa_nome}, o seu histórico de crédito, o qual abrangerá os dados financeiros e de pagamentos relativos às operações de crédito e obrigações de pagamento adimplidas em seus respectivos vencimentos, e aquelas a vencer, constantes de banco(s) de dados, com a finalidade única e exclusiva de subsidiar a análise e a eventual concessão de crédito, a venda a prazo ou outras transações comerciais e empresariais que impliquem risco financeiro, também sendo usado para o {self.empresa_nome}, identificar em qual parceiro credenciado, o cliente irá ser cadastrado.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "5.1. Está ciente de que esta autorização tem validade por tempo indeterminado (somente no caso dos consulentes de que trata o § 2º do art. 8º do Decreto nº 9.936, de 24 de julho de 2019) e que poderá revogar, a qualquer tempo, esta autorização, perante o gestor de banco de dados.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"5.2 Autoriza ao {self.empresa_nome} compartilhar os seus dados pessoais com empresas com as administradoras, com o objetivo de cadastro e acompanhamento da vida útil da sua cota dentro do grupo, agindo como o procurador em nome do cliente, para auxiliar e dar assessoria até o final do contrato vigente dentro da administradora.",
            self.styles['TermoSmallText']
        ))

        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph("<b>6. DECLARAÇÃO DE PEP (PESSOA POLITICAMENTE EXPOSTA)</b>", self.styles['TermoSmallText']))

        elements.append(Paragraph(
            "O (A) Consorciado(a), algum familiar (pai, mãe, filho, filha, cônjuge, companheiro, companheira, enteado, enteada) ou outras pessoas do seu relacionamento próximo, desempenham ou já desempenharam nos últimos 5 (cinco) anos, no Brasil ou em outros países, territórios e dependências estrangeiras função em empresa de serviço público (executivo, legislativo ou judiciário), nos âmbitos Federal, Estadual ou Municipal? (X) Não ( ) Sim",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"7. Afirmo ciência quanto a responsabilidade de comunicação imediata, sobre quaisquer alterações nos seus dados cadastrais perante o {self.empresa_nome}, em especial: endereço residencial, e-mail, telefone e dados relativos à conta bancária, mesmo se for excluído do grupo. Declaro ainda que a última constante na base cadastral será reputada válida para todos os fins, inclusive judiciais.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "8. Declaro ainda, veracidade das informações prestadas, sobre a licitude de sua renda, faturamento e patrimônio, bem como a ciência da Lei nº 9.613|98 e artigos 297, 298, 299 do código penal, no início ou durante o relacionamento.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"9. A atuação do {self.empresa_nome}, fica restrito a administração acompanhamento do cliente durante todo o decorrer do contrato junto a administradora devidamente credenciada e fiscalizada pelo Banco Central, não se responsabilizando ou se solidarizando sobre a referido negocio. O CONTRATANTE/CONSÓRCIADO PARA FINS DE EXECUÇÃO DESTE CONTRATO, CONFERE PODERES AO {self.empresa_nome}, PARA ESCOLHA DA ADMININISTRADORA DE CONSÓRCIO, DEVIDAMENTE AUTORIZADO PELO BANCO CENTRAL, QUE MELHOR SE ENQUADRE NO PERFIL E QUE ATENDA A SEUS OBJETIVOS.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "9.1. O(A) CONTRATANTE, para fins de execução deste CONTRATO, confere poderes a empresa CONTRATADA (intermediadora), para escolha de uma administradora de consórcios, devidamente autorizada pelo poder público, que melhor atenda a seus objetivos. Outorga amplos poderes de representação perante quaisquer administradoras de consórcios, podendo fazer cotações e levantamentos, assinar propostas, contratos, adendos, aditivos, enviar documentos, fazer pesquisas cadastrais, prestar declarações e informações para administradoras com as quais negociar em seu nome, transigir, celebrar contratos, oferecer lances, comparecer em assembleias e nelas votar.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"9.2. O(A) CONTRATANTE autoriza ao {self.empresa_nome}, às administradoras de consórcios parceiras, de forma direta ou através de seus prestadores de serviços, a formar banco de dados com suas informações para a execução deste contrato, consultar SRC do Banco Central do Brasil, SPC, Serasa e similares.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "10. Concorda integralmente com os termos e condições do regulamento de participação em grupo de consórcio, que recebeu nesta data e o qual aceita sem ressalvas, por livre e espontânea vontade, e para tanto, assino o presente CONTRATO DE ADESÃO, em 2 (duas) vias de igual teor.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "11. Este documento poderá ser emitido de forma física, com as assinaturas das partes e testemunhas, se houver, ao final, ou de forma eletrônica, reconhecida pelo ordenamento jurídico brasileiro, nos termos do §5º do artigo 29 da Lei nº 10.931/2004 e do §2º do artigo 10 da MP 2200-2/2001, sendo plenamente válida e aceita pelas PARTES ENVOLVIDAS.",
            self.styles['TermoSmallText']
        ))

        elements.append(PageBreak())

    def _create_page3(self, elements):
        """Página 3 - Declarações finais e assinaturas"""
        self._create_header(elements)

        elements.append(Paragraph(
            "O CONSORCIADO, sob as penas da lei e de anulação deste contrato, DECLARA estar ciente que:",
            self.styles['TermoBodyText']
        ))

        elements.append(Paragraph(
            "a. Para os planos de IMÓVEIS após contemplação, o consorciado contemplado terá direito de utilizar o respectivo crédito de sua cota para compra de qualquer imóvel comercial, residencial, terreno ou construção, conforme regulamento do consórcio.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "b. Para os planos de BENS MÓVEIS após contemplação, o consorciado contemplado terá direito de utilizar o respectivo crédito de sua cota para compra de qualquer bem móvel, tais como: carro, moto, caminhão e ônibus com alienação fiduciária em favor da administradora parceria devidamente credenciada pelo Banco Central, conforme regulamento do consórcio.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "c. Para os planos de ELETRO após contemplação, o consorciado contemplado terá direito de utilizar o respectivo crédito de sua cota para compra de qualquer bem móvel durável, novo, conforme regulamento do consórcio.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "d. Para os planos de SERVIÇOS após contemplação, o consorciado contemplado terá direito de utilizar o respectivo crédito de sua cota para contratação de serviço de qualquer natureza, conforme regulamento do consórcio.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "e. O valor do crédito sofre reajustes anuais de acordo com os índices que medem variações de preços do mercado. Nos planos de imóveis são considerados os índices de variação do INCC – Índice Nacional de Custos da Construção e para os demais planos são considerados os índices do IPCA – Índice de Preços ao Consumidor Amplo ou outros que vierem a substituí-los.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"f. O {self.empresa_nome} e seus parceiros credenciados NÃO comercializa cotas contempladas e todas as contemplações ocorrerão somente por SORTEIO apurado com base na Extração da Loteria Federal ou LANCE, sendo considerado vencedor o que representar maior percentual de quitação ou amortização do crédito, conforme o regulamento.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"g. O pagamento referente à 1ª parcela do consórcio, antecipação de taxa administrativa, serviços {self.empresa_nome} e adicionais {self.empresa_nome}, deverão ser efetuados somente através de boleto bancário, pix ou depósitos feitos diretamente para o {self.empresa_nome}, jamais poderão ser efetuados pagamentos para colaboradores ou supostos cobradores.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "h. Após contemplação será realizada uma análise de crédito, sendo que, se houver alguma negativação nos órgãos de proteção ou qualquer restrição creditícia, bem como se os documentos fornecidos não atenderem às política da Administradora parceria a qual o cliente foi cadastrado, o crédito poderá ser negado ou ficará a cargo dela solicitar avalistas ou garantias complementares para nova análise sem obrigatoriedade de aprovação. Mas o cliente não perderá o direito de uso, enquanto a cota estiver adimplente.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "i. Em caso de desistência ou cancelamento por inadimplência, a devolução dos valores pagos (com dedução das taxas contratadas) se dará através da contemplação da cota ou em até 30(trinta) dias após o encerramento do grupo via transferência bancária para conta da titularidade do consorciado, conforme determinado na Lei 1.795/08.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            f"j. Recebeu a segunda via do contrato de adesão, o regulamento de consórcio e tenho ciência que as responsabilidades tanto do {self.empresa_nome}, tanto da administradora devidamente fiscalizada pelo Banco Central, se limitam ESTRITAMENTE nas descritas no regulamento de consórcio, tornando-se inválidas qualquer promessa, acordo verbal ou escrito pelo vendedor.",
            self.styles['TermoSmallText']
        ))

        elements.append(Paragraph(
            "k. Não houve promessa ou garantia de contemplação nos primeiros meses ou em qualquer outro mês durante a sua permanência no grupo.",
            self.styles['TermoSmallText']
        ))

        elements.append(Spacer(1, 0.4*cm))

        # Data e representante
        rep_nome = self.usuario.nome if self.usuario else ''
        empresa_nome = self.empresa.nome_fantasia if self.empresa else self.empresa_nome

        data_rep = [
            [f"DATA: {self.data_formatada}", f"Representante: {empresa_nome}", "vendedor:"],
        ]
        t_data = Table(data_rep, colWidths=[5.8*cm, 5.8*cm, 5.8*cm])
        t_data.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_data)

        # Espaço para assinaturas
        elements.append(Spacer(1, 1*cm))

        sig_data = [
            ["_" * 40, "_" * 40],
            ["ASSINATURA DO REPRESENTANTE", "ASSINATURA DO CONSORCIADO"],
        ]
        t_sig = Table(sig_data, colWidths=[8.7*cm, 8.7*cm])
        t_sig.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_sig)

        # Aviso
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(
            "ATENÇÃO: NÃO HÁ GARANTIA DE DATA DE CONTEMPLAÇÃO",
            self.styles['TermoWarning']
        ))

        elements.append(Spacer(1, 0.3*cm))

        aviso_data = [
            ["Este contrato somente será válido mediante pagamento e assinatura digital do cliente e do representante."],
        ]
        t_aviso = Table(aviso_data, colWidths=[17.4*cm])
        t_aviso.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_aviso)

    def generate(self):
        """Gera o PDF do termo de adesão e retorna os bytes"""
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

        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        buffer.seek(0)
        return buffer.getvalue()
