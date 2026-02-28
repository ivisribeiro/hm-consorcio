"""
Gerador de PDF - Contrato de Venda
Capital Brasil - Documento de 10 paginas
Layout moderno com cards arredondados via WeasyPrint
"""
import os
import sys

if sys.platform == 'darwin':
    os.environ.setdefault('DYLD_LIBRARY_PATH', '/opt/homebrew/lib')

import weasyprint
import base64
from datetime import datetime


class ContratoVendaPDFGenerator:
    """Gera PDF do Contrato de Venda (10 paginas) - Layout moderno com WeasyPrint"""

    def __init__(self, cliente, beneficio, representante=None, empresa=None):
        self.cliente = cliente
        self.beneficio = beneficio
        self.representante = representante
        self.empresa = empresa

        self.data_atual = datetime.now()
        self.data_formatada = self.data_atual.strftime("%d/%m/%Y %H:%M:%S")

        ano = self.data_atual.year
        self.numero_contrato = f"{ano}{str(beneficio.id).zfill(5)}"

        # Valor da parcela
        self.valor_primeira_parcela = float(beneficio.parcela or 0)

        # Valor intermediação vem da tabela de crédito
        valor_intermediacao = 0
        if hasattr(beneficio, 'tabela_credito') and beneficio.tabela_credito:
            valor_intermediacao = float(beneficio.tabela_credito.valor_intermediacao or 0)

        # Taxa de serviço = valor intermediação
        self.taxa_servico = valor_intermediacao

        # Valor adesão = intermediação + parcela
        self.valor_adesao = valor_intermediacao + self.valor_primeira_parcela

        self.local = f"{(cliente.cidade or 'SAO PAULO').upper()} - {(cliente.estado or 'SP').upper()}"
        self.logo_b64 = self._load_logo_base64()

    # ===================== HELPERS =====================

    def _load_logo_base64(self):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo-capital-brasil.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return ''

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
        sexo = getattr(self.cliente, 'sexo', None)
        if sexo == 'masculino':
            return 'MASCULINO'
        elif sexo == 'feminino':
            return 'FEMININO'
        return sexo.upper() if sexo else ''

    def _get_tipo_bem(self):
        tipo = self.beneficio.tipo_bem
        tipos = {'imovel': 'IMOVEL', 'carro': 'AUTOMOVEL', 'moto': 'MOTOCICLETA'}
        return tipos.get(tipo, tipo.upper() if tipo else '')

    def _get_data_extenso(self):
        meses = ['JANEIRO', 'FEVEREIRO', 'MARCO', 'ABRIL', 'MAIO', 'JUNHO',
                 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        dia = self.data_atual.day
        mes = meses[self.data_atual.month - 1]
        ano = self.data_atual.year
        return f"{dia} de {mes} de {ano}"

    def _safe(self, obj, field, default=''):
        return getattr(obj, field, default) or default

    # ===================== CSS =====================

    def _get_css(self):
        return """
        @page {
            size: A4;
            margin: 0;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: Arial, Helvetica, sans-serif;
            color: #1a1a1a;
            font-size: 8pt;
            line-height: 1.28;
        }

        .page {
            width: 210mm;
            height: 297mm;
            padding: 8mm 12mm;
            page-break-after: always;
            position: relative;
        }
        .page:last-child { page-break-after: auto; }

        /* ---- Footer (absolute at bottom) ---- */
        .footer {
            position: absolute;
            bottom: 6mm;
            left: 12mm;
            right: 12mm;
            display: flex;
            justify-content: space-between;
            font-size: 6.5pt;
            color: #999;
            border-top: 0.5px solid #ddd;
            padding-top: 1.5mm;
        }

        /* ---- Header ---- */
        .header {
            display: flex;
            align-items: flex-start;
            gap: 5mm;
            margin-bottom: 2mm;
        }
        .brand { width: 32mm; }
        .brand img { width: 30mm; display: block; }
        .title { flex: 1; text-align: center; }
        .title h1 {
            font-size: 9pt; font-weight: 800;
            letter-spacing: .3px; line-height: 1.25;
            text-transform: uppercase;
        }
        .divider {
            height: 1.5px; background: #178AA0;
            margin: 2mm 0;
        }

        /* ---- Intro ---- */
        .intro {
            font-size: 7.2pt; line-height: 1.3;
            text-align: justify; margin-bottom: 2.5mm;
        }

        /* ---- Pill row ---- */
        .pill-row {
            display: flex; align-items: center;
            justify-content: space-between;
            gap: 3mm; margin-bottom: 1.2mm;
        }
        .pill {
            flex: 1;
            background: #DCEBEC;
            border-radius: 999px;
            padding: 1.5mm 3.5mm;
            font-weight: 800; font-size: 6.5pt;
            letter-spacing: .2px; text-transform: uppercase;
        }
        .contract-no {
            font-size: 7.5pt; font-weight: 800;
            white-space: nowrap;
        }

        /* ---- Card ---- */
        .card {
            background: #DCEBEC;
            border-radius: 6mm;
            padding: 3mm 4mm;
            margin-bottom: 2mm;
        }

        /* ---- Row layout (horizontal fields) ---- */
        .row {
            display: flex;
            gap: 3mm;
            margin-bottom: 1.5mm;
        }
        .row:last-child { margin-bottom: 0; }
        .row .field { flex: 1; }
        .row .field.w2 { flex: 2; }
        .row .field.w3 { flex: 3; }
        .row .field.w05 { flex: 0.5; }
        .row .field.w15 { flex: 1.5; }

        /* ---- Grid helpers ---- */
        .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.5mm 4mm; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5mm 4mm; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5mm 4mm; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5mm 6mm; }

        /* ---- Field ---- */
        .field { font-size: 7.5pt; line-height: 1.2; }
        .label { font-weight: 800; font-size: 6.2pt; text-transform: uppercase; color: #222; margin-bottom: 0.3mm; }
        .value { font-weight: 400; color: #1a1a1a; font-size: 7.5pt; }

        /* ---- Receipt ---- */
        .receipt-text {
            font-size: 7.5pt; line-height: 1.28;
            text-align: justify; margin-bottom: 1.5mm;
        }
        .sig-label { font-size: 6.5pt; font-weight: 700; margin-bottom: 0.5mm; color: #222; }
        .sig-line {
            height: 5mm; border-radius: 999px;
            background: #fff; margin-bottom: 2mm;
        }

        /* ---- Clause card ---- */
        .clause-card {
            background: #DCEBEC;
            border-radius: 6mm;
            padding: 3.5mm 4.5mm;
            margin-bottom: 2.5mm;
        }
        .clause-title {
            font-weight: 800; font-size: 8pt;
            margin-bottom: 1.5mm; text-transform: uppercase;
            color: #178AA0;
        }
        .clause-text {
            font-size: 7.5pt; text-align: justify;
            line-height: 1.3; margin-bottom: 1.5mm;
        }
        .clause-text:last-child { margin-bottom: 0; }

        /* ---- Declaration card ---- */
        .decl-card {
            background: #DCEBEC;
            border-radius: 6mm;
            padding: 4mm 5mm;
            margin-bottom: 3mm;
        }
        .decl-card p {
            font-size: 7.5pt; text-align: justify;
            line-height: 1.3; margin-bottom: 2.5mm;
        }
        .decl-card p:last-child { margin-bottom: 0; }

        /* ---- Client info (compact, horizontal) ---- */
        .client-info {
            background: #DCEBEC;
            border-radius: 5mm;
            padding: 2.5mm 4mm;
            margin-bottom: 1.5mm;
        }
        .client-info .ci-row {
            display: flex; gap: 3mm;
        }
        .client-info .ci-field { flex: 1; }
        .client-info .ci-label { font-weight: 800; font-size: 6pt; text-transform: uppercase; color: #222; margin-bottom: 0.2mm; }
        .client-info .ci-value { font-size: 7.5pt; font-weight: 400; }

        /* ---- Signature section ---- */
        .sig-section {
            margin-top: 3mm;
        }
        .sig-section .sig-row {
            display: flex; gap: 8mm; margin-bottom: 1.5mm;
        }
        .sig-section .sig-col {
            flex: 1; text-align: center;
        }
        .sig-section .sig-col-label {
            font-size: 6.5pt; margin-bottom: 1mm; color: #222;
        }
        .sig-section .sig-col-line {
            height: 6mm; border-radius: 999px;
            background: #DCEBEC;
        }
        .sig-section .sig-col-name {
            font-size: 7pt; font-weight: 700;
            margin-top: 1mm;
        }

        /* ---- Red warning ---- */
        .red-warning {
            color: #D32F2F; font-weight: 800;
            font-size: 9pt; text-align: center;
            letter-spacing: .4px; margin: 2.5mm 0;
        }

        /* ---- Date box ---- */
        .date-box {
            background: #DCEBEC;
            border-radius: 5mm;
            padding: 3mm 5mm;
            text-align: center;
            margin: 2.5mm 0;
        }

        /* ---- Questionnaire ---- */
        .quest-card {
            background: #DCEBEC;
            border-radius: 6mm;
            padding: 3.5mm 4.5mm;
            margin-bottom: 2.5mm;
        }
        .quest-card p {
            font-size: 7.5pt; text-align: justify;
            line-height: 1.3; margin-bottom: 2mm;
        }
        .quest-card p:last-child { margin-bottom: 0; }

        /* ---- Section title (bordered) ---- */
        .section-title {
            text-align: center; font-weight: 800;
            font-size: 8.5pt; padding: 2.5mm 0;
            border: 1.5px solid #178AA0;
            border-radius: 5mm;
            margin-bottom: 3mm;
            color: #178AA0;
        }

        /* ---- Utility ---- */
        .text-center { text-align: center; }
        .bold { font-weight: 800; }
        .mb-1 { margin-bottom: 1mm; }
        .mb-2 { margin-bottom: 2mm; }
        .mb-3 { margin-bottom: 3mm; }
        .spacer { height: 3mm; }
        .spacer-lg { height: 6mm; }
        """

    # ===================== SHARED COMPONENTS =====================

    def _footer_html(self, page_num):
        return f'<div class="footer"><div></div><div>Pagina {page_num} de 10</div></div>'

    def _client_info_html(self):
        c = self.cliente
        return f"""
        <div class="client-info">
            <div class="ci-row mb-1">
                <div class="ci-field" style="flex:2.5;"><div class="ci-label">Nome</div><div class="ci-value">{c.nome or ''}</div></div>
                <div class="ci-field"><div class="ci-label">CPF</div><div class="ci-value">{self._format_cpf(c.cpf)}</div></div>
                <div class="ci-field"><div class="ci-label">RG</div><div class="ci-value">{self._safe(c, 'identidade')}</div></div>
            </div>
            <div class="ci-row">
                <div class="ci-field" style="flex:2.5;"><div class="ci-label">Local / Data</div><div class="ci-value">SAO PAULO-SP, {self._get_data_extenso()}.</div></div>
                <div class="ci-field" style="flex:2;"><div class="ci-label">Assinatura do consorciado / Conforme documento</div><div style="height:5mm; border-bottom: 0.5px solid #999; margin-top:1mm;"></div></div>
            </div>
        </div>
        """

    def _sig_vendedor_cliente_html(self):
        rep_nome = self.representante.razao_social.upper() if self.representante and self.representante.razao_social else ''
        cliente_cpf = f"{(self.cliente.nome or '').upper()} - {self._format_cpf(self.cliente.cpf)}"
        return f"""
        <div class="sig-section">
            <div class="sig-row">
                <div class="sig-col">
                    <div class="sig-col-label">Nome legivel do Vendedor</div>
                    <div class="sig-col-line"></div>
                    <div class="sig-col-name">{rep_nome}</div>
                </div>
                <div class="sig-col">
                    <div class="sig-col-label">Nome do cliente + CPF do cliente</div>
                    <div class="sig-col-line"></div>
                    <div class="sig-col-name">{cliente_cpf}</div>
                </div>
            </div>
        </div>
        """

    # ===================== PAGE BUILDERS =====================

    def _page_1_html(self):
        c = self.cliente
        b = self.beneficio
        r = self.representante
        e = self.empresa

        # Empresa = razão social do representante
        empresa_nome = r.razao_social if r and r.razao_social else ''
        rep_nome = r.nome if r else ''

        endereco_rua = self._safe(c, 'logradouro')
        endereco_cep = self._safe(c, 'cep')
        endereco_full = f"{endereco_rua}, {endereco_cep}" if endereco_rua else endereco_cep
        naturalidade = self._safe(c, 'naturalidade') or f"{(c.cidade or 'SAO PAULO').upper()} - {(c.estado or 'SP').upper()}"

        logo_html = f'<img src="data:image/png;base64,{self.logo_b64}" style="width:30mm;" />' if self.logo_b64 else ''

        return f"""
        <div class="page">
            <header class="header">
                <div class="brand">{logo_html}</div>
                <div class="title">
                    <h1>CONTRATO DE CONSULTORIA E SERVICOS DIGITAIS PARA<br/>
                    ADESAO A GRUPO DE CONSORCIO DE BENS MOVEIS E<br/>
                    IMOVEIS, NAO CONTEMPLADOS</h1>
                </div>
                <div style="width:32mm;"></div>
            </header>

            <div class="divider"></div>

            <p class="intro">
                Por este instrumento particular de CONTRATO, de um lado, a empresa CAPITAL BRASIL SOLUCOES FINANCEIRAS, pessoa juridica de direito
                privado, inscrita no CNPJ sob o no 60.093.496/0001-17, com sede na Avenida Paulista, 1636, Conj 1504 - Bela Vista, Sao Paulo - SP, CEP 01310-20,
                e-mail atendimento@capitalbanq.com.br, neste ato representado por seu representante legal, doravante denominado simplesmente
                "CONTRATADA", e, de outro lado, o(a) cliente abaixo identificado(a), doravante denominado(a) simplesmente "CONTRATANTE", tem entre si
                justos e contratados o que segue, nos termos e condicoes abaixo:
            </p>

            <div class="pill-row">
                <div class="pill">DADOS CADASTRAIS (OBRIGATORIO PREENCHER TODOS OS CAMPOS) - CONTRATANTE</div>
                <div class="contract-no">No {self.numero_contrato}</div>
            </div>
            <section class="card">
                <div class="row">
                    <div class="field w2"><div class="label">Nome / Razao Social</div><div class="value">{c.nome or ''}</div></div>
                    <div class="field"><div class="label">Data Nascimento</div><div class="value">{self._format_date(getattr(c, 'data_nascimento', None))}</div></div>
                    <div class="field w05"><div class="label">Sexo</div><div class="value">{self._get_sexo()}</div></div>
                    <div class="field"><div class="label">CPF / CNPJ</div><div class="value">{self._format_cpf(c.cpf)}</div></div>
                </div>
                <div class="row">
                    <div class="field"><div class="label">RG / IE</div><div class="value">{self._safe(c, 'identidade')}</div></div>
                    <div class="field"><div class="label">Data Expedicao</div><div class="value">{self._format_date(getattr(c, 'data_expedicao', None))}</div></div>
                    <div class="field w05"><div class="label">Orgao Exp./UF</div><div class="value">{self._safe(c, 'orgao_expedidor')}</div></div>
                    <div class="field w15"><div class="label">Profissao</div><div class="value">{self._safe(c, 'cargo') or self._safe(c, 'profissao')}</div></div>
                </div>
                <div class="row">
                    <div class="field"><div class="label">Nacionalidade</div><div class="value">{self._safe(c, 'nacionalidade', 'BRASILEIRA')}</div></div>
                    <div class="field w15"><div class="label">Nome do Conjuge</div><div class="value">{self._safe(c, 'conjuge_nome') or '&mdash;'}</div></div>
                    <div class="field"><div class="label">Nasc. Conjuge</div><div class="value">{self._format_date(getattr(c, 'conjuge_data_nascimento', None)) or '&mdash;'}</div></div>
                    <div class="field"><div class="label">Naturalidade</div><div class="value">{naturalidade}</div></div>
                </div>
            </section>

            <div class="pill-row"><div class="pill">ENDERECO RESIDENCIAL / COMERCIAL</div></div>
            <section class="card">
                <div class="row">
                    <div class="field w3"><div class="label">Rua / Avenida</div><div class="value">{endereco_full}</div></div>
                    <div class="field w05"><div class="label">No</div><div class="value">{self._safe(c, 'numero')}</div></div>
                    <div class="field"><div class="label">Bairro</div><div class="value">{self._safe(c, 'bairro')}</div></div>
                </div>
                <div class="row">
                    <div class="field"><div class="label">Cidade</div><div class="value">{c.cidade or ''}</div></div>
                    <div class="field w05"><div class="label">Estado</div><div class="value">{c.estado or ''}</div></div>
                    <div class="field"><div class="label">Telefone</div><div class="value">{self._safe(c, 'telefone')}</div></div>
                    <div class="field"><div class="label">Telefone 2</div><div class="value">{self._safe(c, 'telefone_secundario') or '&mdash;'}</div></div>
                    <div class="field w15"><div class="label">E-mail</div><div class="value">{c.email or ''}</div></div>
                </div>
            </section>

            <div class="pill-row"><div class="pill">REPRESENTANTE AUTORIZADO</div></div>
            <section class="card">
                <div class="row">
                    <div class="field w2"><div class="label">Empresa</div><div class="value">{empresa_nome}</div></div>
                    <div class="field"><div class="label">Preposto</div><div class="value">{rep_nome}</div></div>
                    <div class="field"><div class="label">Assinatura</div><div style="height:4mm; border-bottom: 0.5px solid #999;"></div></div>
                </div>
            </section>

            <div class="pill-row"><div class="pill">TAXAS E VALORES APROXIMADOS DO PLANO A SER CONTRATADO NA ADMINISTRADORA DE CONSORCIO</div></div>
            <section class="card">
                <div class="row">
                    <div class="field"><div class="label">Prazo Grupo</div><div class="value">{self._safe(b, 'prazo_grupo')}</div></div>
                    <div class="field"><div class="label">Prazo Cota</div><div class="value">{self._safe(b, 'prazo_cota', self._safe(b, 'prazo_grupo'))}</div></div>
                    <div class="field"><div class="label">Valor do Credito</div><div class="value">{self._format_currency(b.valor_credito)}</div></div>
                    <div class="field"><div class="label">Valor Adesao</div><div class="value">{self._format_currency(self.valor_adesao)}</div></div>
                    <div class="field"><div class="label">Indice Correcao</div><div class="value">{self._safe(b, 'indice_correcao', 'INCC')}</div></div>
                </div>
                <div class="row">
                    <div class="field"><div class="label">Fundo de Reserva</div><div class="value">{self._format_percent(getattr(b, 'fundo_reserva', None))}</div></div>
                    <div class="field"><div class="label">Seguro Prestamista</div><div class="value">{self._format_percent(getattr(b, 'seguro_prestamista', None))}</div></div>
                    <div class="field"><div class="label">Tx. Adm. Total</div><div class="value">{self._format_percent(getattr(b, 'taxa_administracao', None))}</div></div>
                    <div class="field"><div class="label">Demais Parcelas</div><div class="value">{self._format_currency(getattr(b, 'valor_demais_parcelas', None) or b.parcela)}</div></div>
                    <div class="field"><div class="label">Tipo do Bem</div><div class="value">{self._get_tipo_bem()}</div></div>
                </div>
                <div class="row">
                    <div class="field"><div class="label">Grupo</div><div class="value">{self._safe(b, 'grupo')}</div></div>
                    <div class="field"><div class="label">Cota</div><div class="value">{self._safe(b, 'cota')}</div></div>
                    <div class="field"><div class="label">Qtde. Participantes</div><div class="value">{self._safe(b, 'qtd_participantes')}</div></div>
                    <div class="field"><div class="label">Tipo Plano</div><div class="value">{self._safe(b, 'tipo_plano', 'NORMAL')}</div></div>
                    <div class="field"></div>
                </div>
            </section>

            <div class="pill-row"><div class="pill">RECIBO E FORMA DO PAGAMENTO INICIAL</div></div>
            <section class="card">
                <p class="receipt-text">Recebemos a importancia de <b>{self._format_currency(self.taxa_servico)}</b> na forma abaixo descrita, sendo este valor referente a intermediacao e prestacao de servicos de consultoria da Capital Brasil, aos quais declara o(a) CONTRATANTE ciente de que nao se trata de Cota contemplada, Financiamento ou Emprestimo.</p>
                <div class="sig-label">Assinatura do(a) contratante</div>
                <div class="sig-line"></div>
                <p class="receipt-text">Recebemos a importancia de <b>{self._format_currency(b.parcela)}</b>, referente a parcela inicial do plano escolhido pela CONTRATANTE. A CONTRATADA se compromete a promover a contratacao da cota adequada na administradora de consorcio e efetuar a sua adesao sem reservas.</p>
                <div class="sig-label">Assinatura do(a) contratante</div>
                <div class="sig-line"></div>
                <p class="receipt-text">Valor do consorcio: <b>{self._format_currency(b.valor_credito)}</b>, referente ao credito total do plano aderido pela CONTRATANTE junto a administradora de consorcio.</p>
                <div class="sig-label">Assinatura do(a) contratante</div>
                <div class="sig-line" style="margin-bottom:0;"></div>
            </section>

            <p class="text-center" style="font-size:7.5pt; margin-top:1mm;">{self.local.upper()}</p>
            {self._footer_html(1)}
        </div>
        """

    def _page_2_html(self):
        c = self.cliente
        b = self.beneficio
        return f"""
        <div class="page">
            <div class="pill-row"><div class="pill">CONTA BANCARIA INDICADA PELO CLIENTE PARA EVENTUAL CONTEMPLACAO / RESTITUICAO DE VALORES</div></div>
            <section class="card">
                <div class="row">
                    <div class="field w15"><div class="label">Banco</div><div class="value">{self._safe(c, 'banco')}</div></div>
                    <div class="field"><div class="label">Tipo de Conta</div><div class="value">{self._safe(c, 'tipo_conta')}</div></div>
                    <div class="field"><div class="label">Agencia</div><div class="value">{self._safe(c, 'agencia')}</div></div>
                    <div class="field w15"><div class="label">Conta</div><div class="value">{self._safe(c, 'conta')}</div></div>
                </div>
                <div class="row">
                    <div class="field"><div class="label">Chave Pix Nominal</div><div class="value">{self._safe(c, 'chave_pix')}</div></div>
                    <div class="field"><div class="label">Seguro Prestamista</div><div class="value">{self._format_percent(getattr(b, 'seguro_prestamista', None))}</div></div>
                </div>
            </section>

            <div class="spacer"></div>

            <div class="clause-card">
                <div class="clause-title">1. DEFINICAO TERMOS TECNICOS</div>
                <p class="clause-text">(i) CONSORCIO: reuniao de pessoas naturais e juridicas em grupo, com prazo de duracao e numero de cotas previamente determinados, promovida por administradora de consorcio, com a finalidade de propiciar a seus integrantes, de forma isonomica, a aquisicao de bens ou servicos, por meio de autofinanciamento, conforme art. 2o da Lei 11.795/08;</p>
                <p class="clause-text">(ii) GRUPO DE CONSORCIO: sociedade nao personificada constituida por consorciados para os fins estabelecidos no art. 2o da Lei 11.795/2008;</p>
                <p class="clause-text">(iii) ADMINISTRADORA DE CONSORCIO: pessoa juridica prestadora de servicos com objeto social principal voltado a administracao de grupos de consorcio, constituida sob a forma de sociedade limitada ou sociedade anonima, nos termos do art. 7o, inciso I da Lei 11.795/2008;</p>
                <p class="clause-text">(iv) INTERMEDIADORA/MANDATARIA: pessoa juridica prestadora dos servicos de intermediacao e assessoramento como a CONTRATADA, visando avaliacao especifica de seu perfil e necessidade para inclusao em um grupo adequado em administradora de consorcios, devidamente autorizada pelo Banco Central do Brasil (BACEN), com acompanhamento ate a contemplacao e aquisicao do bem ou servico pretendido. O objeto da INTERMEDIADORA/MANDATARIA se constitui de obrigacao de meio e nao de resultado, nao garantindo contemplacao;</p>
                <p class="clause-text">(v) CONSORCIADO: pessoa natural ou juridica integrante de grupo de consorcio;</p>
                <p class="clause-text">(vi) COTA: fracao ideal do grupo atribuida a cada consorciado;</p>
                <p class="clause-text">(vii) CONTEMPLACAO: atribuicao ao consorciado do direito de utilizar o credito para a aquisicao do bem ou servico, por meio de sorteio ou lance.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">2. OBJETO</div>
                <p class="clause-text">2.1. O presente CONTRATO tem por objeto a prestacao de servicos de intermediacao especializados, pela CONTRATADA, na prospeccao/negociacao entre o CONTRATANTE e as administradoras de grupos de consorcio, visando o levantamento de perfil, necessidade e adesao a grupo de consorcio, fornecendo, ainda, suporte ate a efetivacao de sua contemplacao e entrega do bem.</p>
                <p class="clause-text">2.1.1. A atuacao da CONTRATADA, fica restrita a mediacao e/ou intermediacao da relacao juridica entre o CONTRATANTE e a administradora do grupo de consorcio, nao se responsabilizando ou se solidarizando sobre o referido negocio. Todas as parcelas e taxas devidas a Administradora de Consorcio sao responsabilidade da CONTRATANTE.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">3. MANDATO</div>
                <p class="clause-text">3.1. O(A) CONTRATANTE, para fins de execucao deste CONTRATO, confere poderes a empresa CONTRATADA (Capital Brasil), para escolha de uma administradora de consorcios, devidamente autorizada pelo poder publico, que melhor atenda a seus objetivos. Outorga amplos poderes de representacao perante quaisquer administradoras de consorcios, podendo fazer cotacoes e levantamentos, assinar propostas, contratos, adendos, aditivos, enviar documentos, fazer pesquisas cadastrais, prestar declaracoes e informacoes para administradoras com as quais negociar em seu nome, transigir, celebrar contratos, oferecer lances, comparecer em assembleias e nelas votar.</p>
                <p class="clause-text">3.2. O(A) CONTRATANTE autoriza ao Capital Brasil, as administradoras de consorcios parceiras, de forma direta ou atraves de seus prestadores de servicos, a formar banco de dados com suas informacoes para a execucao deste contrato, consultar SRC do Banco Central do Brasil, SPC, Serasa e similares.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">4. OBRIGACOES DA CONTRATADA</div>
                <p class="clause-text">4.1. Aproximar o(a) CONTRATANTE de uma Administradora de consorcio, indicar e aloca-lo(a) em um grupo de consorcio que melhor atenda o seu perfil, no prazo de 30 (trinta) dias a contar da data da assinatura do presente CONTRATO.</p>
                <p class="clause-text">4.1.1. A administradora escolhida, obrigatoriamente, devera ser autorizada pelo Banco Central do Brasil (BACEN).</p>
                <p class="clause-text">4.2. Prestar o atendimento inicial e no transcorrer do grupo, fornecendo suporte ao(a) CONTRATANTE, ate a efetivacao de sua contemplacao e a entrega do bem.</p>
                <p class="clause-text">4.2.1. O atendimento sera prestado, exclusivamente, por meio telefonico, e-mail e WhatsApp.</p>
                <p class="clause-text">4.2.2. Quando da contemplacao da cota, auxiliar no faturamento do bem ou servico junto a administradora.</p>
            </div>

            {self._footer_html(2)}
        </div>
        """

    def _page_3_html(self):
        return f"""
        <div class="page">
            <div class="clause-card">
                <div class="clause-title">5. OBRIGACOES DA CONTRATANTE</div>
                <p class="clause-text">5.1. Fazer cumprir o negocio juridico aqui celebrado, com a plena ciencia das clausulas deste CONTRATO e demais anexos que os acompanham, devidamente assinados.</p>
                <p class="clause-text">5.2. Se portar de acordo com a boa-fe, com integridade e confiabilidade para nao frustrar a execucao deste contrato. Qualquer prejuizo por informacoes falsas ou inexatas por parte da CONTRATANTE sera de sua exclusiva responsabilidade. Caso a CONTRATADA sofra prejuizos por informacoes falsas ou inexatas por parte da CONTRATANTE, esta devera se responsabilizar.</p>
                <p class="clause-text">5.3. Manter sempre atualizado o seu endereco, telefone/WhatsApp e PIX, junto a CONTRATADA, informando, por escrito, todas as eventuais alteracoes, sob pena de perda de prazos e frustracao da execucao deste contrato, os quais sob nenhuma hipotese sera responsabilidade da CONTRATADA.</p>
                <p class="clause-text">5.4. Apos o seu ingresso ao grupo de consorcio, se obriga a respeitar todas as clausulas do CONTRATO de adesao e normativos vigentes, bem como contatar a CONTRATADA, sempre que houver duvida ou esclarecimentos quanto ao negocio pactuado, bem como ao funcionamento do consorcio.</p>
                <p class="clause-text">5.5. Efetuar o pagamento das parcelas contratadas com absoluta pontualidade.</p>
                <p class="clause-text">5.6. Efetuar a assinatura de documentos da contratacao, ofertas de lance, faturamento, de acordo com os prazos consignados.</p>
                <p class="clause-text">5.7. O(A) CONTRATANTE declara ter condicoes economico-financeiras para assumir as obrigacoes pretendidas por este contrato, perante o grupo de consorcio, na forma da Resolucao BCB no 285 e 362.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">6. SERVICOS</div>
                <p class="clause-text">6.1. A CONTRATADA atuara de acordo com as especificacoes descritas neste instrumento, com etica e responsabilidade. A CONTRATADA, como mandataria da CONTRATANTE, devera prestar informacoes acerca das pesquisas, negociacoes, aprovacoes de cadastros, clausulas de contratos, condicionantes de cada proposta, contemplacao e faturamento de bens.</p>
                <p class="clause-text">6.2. O servico prestado corresponde a intermediacao e/ou mediacao entre o(a) CONTRATANTE e a administradora do grupo de consorcio quanto a aquisicao de cota de participacao, sem que a CONTRATADA realize qualquer ato de administracao de cotas de consorcio.</p>
                <p class="clause-text">6.2.1. O presente instrumento nao se confunde com contrato de adesao a grupo de consorcio, nem com financiamento ou qualquer outra contratacao protegida pelo sistema financeiro, tendo carater exclusivamente de intermediacao e assessoria para a adesao em grupo de consorcio e prestacao dos servicos de orientacao, ate a contemplacao da cota e entrega do bem.</p>
                <p class="clause-text">6.3. Nao constitui obrigacao da CONTRATADA a realizacao da venda de cota de participacao em grupo de consocios para terceiros.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">7. PAGAMENTO</div>
                <p class="clause-text">7.1. O pagamento referente ao item RECIBO se refere a servicos de consultoria da CONTRATADA, que devera ser efetuado somente atraves de boleto bancario, pix ou depositos feitos diretamente para o Capital Brasil. Jamais poderao ser efetuados pagamentos para colaboradores ou supostos cobradores que nao seja o proprio Capital Brasil. O valor referente a parcela do consorcio sera repassado a Administradora apos a sua aprovacao.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">8. PRAZO DO CONTRATO</div>
                <p class="clause-text">8.1. Os direitos e obrigacoes iniciam a partir do pagamento total a titulo de taxa de servico da Capital Brasil e vigera ate a data da contemplacao e faturamento do bem ou servicos.</p>
                <p class="clause-text">8.1.1. Na hipotese de desistencia, pelo(a) CONTRATANTE, apos a participacao em assembleia ordinaria de distribuicao de bens, no grupo de consorcio e antes de sua contemplacao, o presente instrumento vigera ate a contemplacao da cota desistente, sendo obrigacao da CONTRATADA, acompanhar e conferir o calculo dos valores a serem restituidos ao(a) CONTRATANTE.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">9. RESCISAO E DEVOLUCAO</div>
                <p class="clause-text">9.1. O presente CONTRATO e celebrado por prazo determinado, contemplacao da cota e entrega do bem ou em caso de desistencia do consorcio, a contemplacao da cota por desistencia, podendo, com antecedencia de 30 (trinta) dias, ser denunciado unilateralmente. A denuncia devera ser encaminhada por escrito e com protocolo de recebimento.</p>
            </div>

            {self._footer_html(3)}
        </div>
        """

    def _page_4_html(self):
        return f"""
        <div class="page">
            <div class="clause-card">
                <div class="clause-title">9. RESCISAO E DEVOLUCAO (cont.)</div>
                <p class="clause-text">9.1.1. Ocorrendo a rescisao pelo CONTRATANTE, este declara ciente que nao tera direito a restituicao ao valor pago a titulo de assessoria, visto que, alem dos servicos prestados ate a data da rescisao, a CONTRATADA permanecera na obrigacao do acompanhamento da cota ate a contemplacao do(a) CONTRATANTE, junto a administradora de consorcio.</p>
                <p class="clause-text">9.1.2. Caso o(a) CONTRATANTE rescinda ou desista da participacao no grupo de consorcio, independente do motivo, este declara ciente que tera direito a restituicao apenas dos valores comprovadamente transferidos e ja pagos a administradora do grupo de consorcio e somente recebera quando da contemplacao da cota desistente, nos termos dos artigos 22 e 30, da Lei Federal 11.795/08.</p>
                <p class="clause-text">9.1.3. Caso a parte denunciante seja a CONTRATADA, a resilicao contratual representara a devolucao integral do valor pago a titulo da assessoria, devidamente corrigido pelo INPC, decotado os valores, comprovadamente, transferidos a administradora de consorcio, permanecendo o(a) CONTRATANTE com as obrigacoes decorrentes de sua participacao no grupo de consorcio.</p>
                <p class="clause-text">9.2. O(A) CONTRATANTE podera rescindir unilateralmente o presente instrumento, por meio de carta escrita de proprio punho, sem necessidade de justificativa, no prazo de ate 7 (sete) dias, em conformidade com a Lei Federal no 8.078/90 (Codigo de Defesa do Consumidor), com direito a restituicao integral do valor de adesao pago, desde que respeitado o disposto na clausula 9.3.</p>
                <p class="clause-text">9.3. Caso a rescisao ocorra apos 24 (vinte e quatro) horas da assinatura deste contrato, sera aplicada uma multa rescisoria de ate 20% (vinte por cento) do valor pago, a titulo de custos operacionais e administrativos, descontada dos valores a serem restituidos ao(a) CONTRATANTE.</p>
                <p class="clause-text">9.4. Em caso de cancelamento realizado dentro do prazo legal de 7 (sete) dias corridos, o valor pago pelo(a) CONTRATANTE sera restituido no prazo maximo de ate 30 (trinta) dias uteis, contados a partir da data da solicitacao formal de cancelamento, descontando-se 20% (vinte por cento) do montante total, a titulo de taxa administrativa da intermediadora, destinada a cobrir os custos operacionais e de intermediacao ja realizados.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">10. INDEPENDENCIA ENTRE AS CLAUSULAS</div>
                <p class="clause-text">10.1. A nao validade, no todo ou em parte, de qualquer disposicao deste instrumento, nao afetara a validade ou a responsabilidade de quaisquer das outras clausulas.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">11. CONFIDENCIALIDADE - CLAUSULA PENAL</div>
                <p class="clause-text">11.1. As partes se obrigam em manter a confidencialidade de toda a relacao negocial deste instrumento e convencionam a titulo de clausula penal o pagamento, a quem der causa, de multa pecuniaria correspondente ao valor de 10 (dez) vezes ao pagamento total inicial (item 3), devidamente atualizado pelo INCC, a epoca do descumprimento.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">12. DISPOSICOES GERAIS</div>
                <p class="clause-text">12.1. Este CONTRATO e as clausulas que o compoem nao poderao se emendados, cancelados, abandonados ou alterados em qualquer forma, exceto atraves de acordo mutuo, firmado pelas partes.</p>
                <p class="clause-text">12.2. Este CONTRATO, uma vez firmado pelas partes, constituira compromisso irretratavel, irrevogavel, incondicional e o acordo completo e final entre as partes, substituindo todos os pre-entendimentos, compromissos, cartas, mensagens enviadas pelo aplicativo WhatsApp, e-mails ou correspondencias anteriores e em relacao a negociacao, que mediante este contrato foi firmado e aperfeicoado.</p>
                <p class="clause-text">12.3. Cada clausula, paragrafo, frase ou sentenca deste CONTRATO constitui um compromisso ou disposicao independente e distinta. Sempre que possivel, cada clausula deste CONTRATO devera ser interpretada de modo a se tornar valida e eficaz a luz da lei aplicavel.</p>
                <p class="clause-text">12.4. Nenhuma disposicao deste CONTRATO, seja ela expressa ou tacita, tem a intencao ou deve ser interpretada de modo a conferir a terceiros, direta ou indiretamente, qualquer direito, ou direito a recurso ou demanda judicial referente a este instrumento contratual.</p>
                <p class="clause-text">12.5. A tolerancia, por qualquer das partes, com relacao ao descumprimento de qualquer termo ou condicao aqui ajustado, nao sera considerada como desistencia em exigir o cumprimento de disposicao nele contida.</p>
                <p class="clause-text">12.6. Sobrevindo a ocorrencia de casos fortuitos ou forca maior que impossibilitem a execucao dos servicos e que independam da vontade da CONTRATADA, o CONTRATO podera ser suspenso ate que cesse o referido motivo ou encerrado em comum acordo.</p>
                <p class="clause-text">12.7. E defeso a qualquer das partes ceder ou transferir total ou parcial direitos e obrigacoes decorrentes deste CONTRATO, sem autorizacao expressa e por escrito de ambas as partes.</p>
                <p class="clause-text">12.8. O(A) CONTRATANTE reconhece a inexistencia e a exclusao de qualquer especie de responsabilidade por parte da CONTRATADA, referente a todo e qualquer prejuizo, perda, passivo, custo, demanda, que estejam relacionados ao CONTRATO de participacao em grupo de consorcios. As partes se obrigam a observar e cumprir as clausulas do presente CONTRATO, por si, seus herdeiros e/ou sucessores.</p>
                <p class="clause-text">12.9. O(A) CONTRATANTE autoriza expressamente a coleta, tratamento e manutencao de seus dados pela CONTRATADA para a execucao deste contrato.</p>
            </div>

            {self._footer_html(4)}
        </div>
        """

    def _page_5_html(self):
        data_extenso = self._get_data_extenso()
        return f"""
        <div class="page">
            <div class="clause-card">
                <div class="clause-title">13. DECLARACOES E DO CONHECIMENTO PREVIO</div>
                <p class="clause-text">13.1. O(A) CONTRATANTE, neste ato, declara saber que:</p>
                <p class="clause-text">(i) nenhuma promessa ou proposta extracontratual e extra normativos do sistema de consorcios lhe foi feita. Informa que leu atentamente todas as clausulas e condicoes do presente instrumento, obtendo assim, todas as informacoes necessarias para o perfeito conhecimento das regras de funcionamento do produto consorcio e que autoriza sua contabilizacao definitiva na empresa escolhida, sem nenhuma restricao;</p>
                <p class="clause-text">(ii) ALERTA AO CONSUMIDOR: Nenhum documento, promessa escrita, verbal ou gravada, feitas ou firmadas por terceiros, ou mesmo por funcionarios sem poderes de gestao, que nao sejam os representantes legais da CONTRATADA, nao terao nenhuma validade, prevalecendo somente as clausulas contratuais;</p>
                <p class="clause-text">(iii) que autoriza a CONTRATADA a consultar quaisquer informacoes disponibilizadas pelos orgaos de protecao ao credito.</p>
                <p class="clause-text">(iv) Em caso de desistencia por parte da CONTRATANTE, os valores pagos a titulo de intermediacao e assessoria nao poderao ser devolvidos por se tratar de servico ja prestado.</p>
            </div>

            <div class="clause-card">
                <div class="clause-title">14. FORO</div>
                <p class="clause-text">14.1. Para dirimir quaisquer questoes oriundas do presente CONTRATO, as partes elegem o foro da Comarca de Sao Paulo, Estado de Sao Paulo, com renuncia expressa de qualquer outro, por mais privilegiado que seja ou venha a ser.</p>
            </div>

            <div class="spacer-lg"></div>
            <p class="text-center" style="font-size:8.5pt;">SAO PAULO-SP, {data_extenso}.</p>
            <div class="spacer-lg"></div>

            <div class="sig-section">
                <div class="sig-row">
                    <div class="sig-col"><div class="sig-col-label">Assinatura da CONTRATADA</div><div class="sig-col-line"></div></div>
                    <div class="sig-col"><div class="sig-col-label">Assinatura do(a) CONTRATANTE</div><div class="sig-col-line"></div></div>
                </div>
            </div>

            <p class="text-center bold" style="font-size:9pt; margin: 3mm 0;">TESTEMUNHAS</p>
            <div class="sig-section">
                <div class="sig-row">
                    <div class="sig-col"><div class="sig-col-line"></div></div>
                    <div class="sig-col"><div class="sig-col-line"></div></div>
                </div>
            </div>

            <div class="spacer"></div>

            <div class="pill-row"><div class="pill">DECLARACAO DE PESSOA POLITICAMENTE EXPOSTA - PEP</div></div>
            <div class="spacer"></div>

            <p class="clause-text">O objetivo desta declaracao e atender as diretrizes do Banco Central do Brasil Bacen e do COAF/UIF que administradoras de consorcio devem adotar, para controles e acompanhamento dos negocios e movimentacoes financeiras das pessoas politicamente expostas a fim de atender dispostos na lei 9.613 de 3 de Marco de 1998.</p>
            <p class="clause-text">Sao considerados pessoas politicamente expostas Todas aquelas que previstas no artigo 4o da circular do Banco Central do Brasil BACEN de no 3.461 de 24 de julho de 2009 da qual consorciado abaixo-assinado declara ter conhecimento.</p>

            <div class="spacer"></div>
            <p class="clause-text">&#8226; Sou pessoa politicamente exposta __________.</p>
            <p class="clause-text">&#8226; Possuo parentes de primeiro grau pais ou filhos conjuges companheiro, enteado inclusive representante pessoas que possam ter minha a procuracao que possam ser considerados pessoas politicamente expostas __________.</p>
            <p class="clause-text">&#8226; Estou enquadrado como Estreito colaborador de pessoa politicamente exposta como definido pelo COAF __________.</p>

            <div class="spacer"></div>
            <div class="decl-card" style="padding:3mm 5mm;">
                <p style="margin-bottom:0;">Declaro sob as penas da lei que as informacoes aqui prestadas sao expressao da Verdade pelas quais me responsabilizo com a veracidade e exatidao das informacoes prestadas.</p>
            </div>

            <div class="spacer"></div>
            {self._client_info_html()}

            {self._footer_html(5)}
        </div>
        """

    def _page_6_html(self):
        return f"""
        <div class="page">
            <div class="spacer-lg"></div>

            <div class="section-title">DECLARACAO DE CIENCIA</div>

            <div class="decl-card">
                <p>Declaro para os devidos fins de Direito que ao contratar os servicos:</p>
                <p>Tomou ciencia na data de hoje, que do valor pago nessa ocasiao da contratacao sera passado o valor aproximado de <b>{self._format_currency(self.beneficio.parcela)}</b> para a administradora de consorcios, a ser contratada a titulo de primeira parcela do consorcio, e o saldo remanescente sera utilizado para pagamentos de custas de contratacao da intermediacao tais como custas comerciais, e administrativas conforme contrato de intermediacao na adesao a grupo de consorcio nao contemplados. Desde ja fica autorizado tais repasses descritos aqui, atraves dessa declaracao e ratificacao atraves do instrumento particular de contratacao, aditivos e checagem telefonica gravada.</p>
            </div>

            <div class="spacer-lg"></div>
            {self._client_info_html()}

            {self._footer_html(6)}
        </div>
        """

    def _page_7_html(self):
        return f"""
        <div class="page">
            <div class="section-title">TERMO DE CONTRATACAO DE SERVICOS DE CONSULTORIA FINANCEIRA</div>

            <div class="decl-card">
                <p>A Capital Brasil atua exclusivamente na consultoria financeira para aquisicao de consorcios nao contemplados, facilitando a conexao entre o cliente e a administradora de consorcios. Essa consultoria e realizada por meio de seus consultores credenciados, que sao pessoas juridicas autonomas e possuem liberdade para cobrar pelos servicos de atendimento e vendas prestadas.</p>
                <p>O(a) PROPONENTE declara, conforme a lei, que preencheu uma proposta de consultoria financeira com a Capital Brasil para adquirir um consorcio nao contemplado e esta ciente de que deve aguardar a contemplacao por meio de sorteio pela Loteria Federal ou lance, conforme o regulamento geral de consorcios.</p>
                <p>O(a) PROPONENTE esta ciente de que sua proposta sera comprovada pelo setor de qualidade da Capital Brasil e, somente apos validacao, seu contrato sera apresentado a administradora e incluido no grupo de consorcio.</p>
                <p>O(a) PROPONENTE declara ter lido e compreendido todas as clausulas do regulamento do consorcio, em conformidade com a Lei no 11.795/2008, incluindo suas obrigacoes, taxas e formas de contemplacao, e que nao restam duvidas sobre a negociacao assumida.</p>
                <p>O(a) PROPONENTE autoriza que a contratacao de uma consultoria financeira para consorcio nao e obrigatoria, mas aceita livremente os termos e condicoes contratuais propostas.</p>
                <p>O(a) PROPONENTE tambem declara estar ciente de que os valores pagos na adesao referem-se a inclusao no grupo de consorcio, a taxa administrativa da administradora e a taxa de consultoria pela prestacao de servicos da Capital Brasil.</p>
            </div>

            <div class="spacer-lg"></div>
            {self._client_info_html()}

            {self._footer_html(7)}
        </div>
        """

    def _page_8_html(self):
        data_extenso = self._get_data_extenso()
        return f"""
        <div class="page">
            <div class="section-title">TERMO DE CONTRATACAO DE SERVICOS DE CONSULTORIA FINANCEIRA</div>

            <div class="decl-card">
                <p>A Capital Brasil atua como consultora financeira, promovendo a assessoria na aquisicao de consorcios nao contemplados entre o(a) CONTRATANTE e a Administradora de Consorcios, por meio de seus consultores financeiros devidamente credenciados, que possuem independencia para realizar a cobranca pelos servicos prestados de atendimento e vendas.</p>
                <p>O(a) PROPONENTE declara, sob as penas da lei, que preencheu uma proposta de consultoria financeira junto a Capital Brasil com o objetivo de adquirir uma cota de consorcio nao contemplada. O(a) PROPONENTE compreende que a contemplacao ocorrera em conformidade com os termos do regulamento geral da Administradora, seja por sorteio automatico ou por lance, e se obrigara a efetuar o pagamento das parcelas rigorosamente em dia.</p>
                <p>O(a) PROPONENTE esta ciente de que uma proposta sera comprovada pela Administradora de Consorcios e pela Capital Brasil, que podera recusar o caso nao atender as exigencias legais e as politicas internas da Administradora.</p>
                <p>O(a) PROPONENTE declara estar ciente de que o cancelamento do consorcio apos a facilidade da proposta podera gerar prejuizos financeiros a Capital Brasil e aos consultores responsaveis pela intermediacao, comprometendo-se a reparar eventuais perdas e danos, incluindo a garantia da comissao de corretagem para o consultor envolvido na revenda da cota.</p>
                <p>O(a) PROPONENTE confirma ter lido e compreende todas as clausulas do regulamento do consorcio, bem como as obrigacoes e direitos relacionados a contratacao, nao restando duvidas sobre a negociacao assumida, conforme previsto na Lei no 11.795/2008.</p>
                <p>O(a) PROPONENTE autoriza que a contratacao de uma consultoria financeira nao e obrigatoria para a aquisicao de consorcio, mas aceita voluntariamente os termos e condicoes contratuais ou pactuados.</p>
                <p>O(a) PROPONENTE concorda que, dos valores pagos na taxa de adesao, a comissao de corretagem sera repassada aos consultores de consorcios, autorizando desde ja o pagamento sem que isso gere qualquer prejuizo a Capital Brasil.</p>
            </div>

            <div class="red-warning">LEIA COM ATENCAO ANTES DE ASSINAR.</div>

            <div class="date-box">
                <p style="font-size:9pt;">SAO PAULO-SP, {data_extenso}.</p>
                <p class="red-warning" style="margin:1.5mm 0 0 0;">NAO COMERCIALIZAMOS COTAS CONTEMPLADAS.</p>
            </div>

            {self._sig_vendedor_cliente_html()}

            {self._footer_html(8)}
        </div>
        """

    def _page_9_html(self):
        return f"""
        <div class="page">
            <div class="section-title">QUESTIONARIO DE CHECAGEM</div>

            <div class="decl-card" style="text-align:center;">
                <p style="text-align:center;">Parabens pela aquisicao da sua cota de consorcio e um prazer te-lo como cliente!</p>
                <p style="text-align:center;">Esperamos poder contar com a sua colaboracao para que possamos proceder corretamente com o seu cadastro de contrato, e ao mesmo tempo realizar uma avaliacao da qualidade do servico prestado pelo nosso consultor de vendas. Para que isso ocorra pedimos que responda o questionario abaixo com sim ou nao:</p>
            </div>

            <div class="quest-card">
                <p>Voce contratou um servico de Consultora com a Capital Brasil para participar de um consorcio nao contemplado? __________</p>
                <p>Voce confirma que possuiu capacidade financeira para arcar com as prestacoes do seu consorcio? __________</p>
                <p>Voce esta ciente que o valor da sua parcela mensal e de {self._format_currency(self.beneficio.parcela)}? __________</p>
                <p>Tomou ciencia que a empresa Capital Brasil nao administra consorcios, apenas promove a consultoria? __________</p>
                <p>Voce tem ciencia que o consorcio nao esta contemplado? __________</p>
                <p>Foi informado(a) de que a contemplacao ocorrera somente por sorteio ou lance fixo ou lance Livre? __________</p>
                <p>Lhe foi feita alguma promessa de contemplacao, garantia de contemplacao em determinado prazo, mediante determinado valor de lance ou vantagens extras? __________</p>
                <p>Ocorrendo a rescisao pelo CONTRATANTE, este declara ciente que nao tera direito a restituicao ao valor pago a titulo de assessoria, visto que, alem dos servicos prestados ate a data da rescisao, a CONTRATADA permanecera na obrigacao do acompanhamento da cota ate a contemplacao do(a) CONTRATANTE, junto a administradora de consorcio. __________</p>
                <p>Voce leu com atencao todo o contrato de intermediacao para adesao a grupo de consorcio e assinou concordando com as clausulas e condicoes somente depois da leitura? __________</p>
                <p>Voce escolheu participar de um consorcio intermediado pela Capital Brasil e administrado por Administradoras de Consorcios autorizadas e fiscalizadas pelo Banco Central? __________</p>
            </div>

            <p class="clause-text">Promovemos a intermediacao entre o interessado em consorcio e a administradora legalmente autorizadas pelo Banco Central, atraves de seus corretores pessoa Juridica autonomos credenciados.</p>
            <p class="clause-text mb-2">Prezado cliente, os seus dados serao inseridos no sistema da administradora e voce recebera no seu e-mail o regulamento do consorcio adquirido. Voce recebera tambem, seu grupo e a cota.</p>

            {self._sig_vendedor_cliente_html()}

            {self._footer_html(9)}
        </div>
        """

    def _page_10_html(self):
        data_extenso = self._get_data_extenso()
        return f"""
        <div class="page">
            <div class="pill-row"><div class="pill">CIENCIA E CONCORDANCIA COM A ANALISE CREDITICIA PREVIA A AQUISICAO DE COTA DE CONSORCIO</div></div>

            <div class="quest-card">
                <p>1. Estou ciente de que, apos realizacao de uma simulacao na data de assinatura deste, com base em consultas aos orgaos de protecao ao credito, na renda por mim informada e nos documentos por mim apresentados, fui devidamente informado quanto a aprovacao ou reprovacao do credito, no cenario ATUAL, se hoje houvesse a contemplacao de cota, seja por sorteio, seja por lance;</p>
                <p>2. Estou ciente, ainda, de que o cenario ATUAL esta sujeito a mudancas, podendo variar diaria, semanal ou mensalmente, conforme as minhas condicoes pessoais tambem se alterem (profissao, renda, estado civil, restricoes etc.);</p>
                <p>3. Desta forma, estou ciente e de acordo que o status de aprovacao ou reprovacao pode sofrer alteracao a qualquer tempo conforme minhas condicoes pessoais tambem se alterem, sendo que nova analise podera ser realizada no momento da contemplacao;</p>
                <p>4. Por fim, declaro que fui informado sobre a analise crediticia e assinei o presente contrato antes de efetivar a minha adesao a qualquer grupo de consorcio. Declaro que foi ofertado respeitando as leis vigentes em observancia ao Codigo de Defesa do Consumidor e Lei 11.795/2008, deixando claro que a decisao de dar continuidade na compra foi minha, ciente dos prazos e regulamentos atuais.</p>
                <p>Declaro expressamente de estar ciente que em decorrencia da minha incapacidade financeira junto as instituicoes de credito, as quais indeferiram a aquisicao mediante financiamento do bem, autorizo a contratada a proceder com a aquisicao do bem por meio de aquisicao de cotas de participacao em grupo de consorcio, nos termos elencados no contrato que me foi fornecido e cientificado das clausulas com a devia antecedencia.</p>
            </div>

            <div class="red-warning">LEIA COM ATENCAO ANTES DE ASSINAR.</div>

            <div class="date-box">
                <p style="font-size:9pt;">SAO PAULO-SP, {data_extenso}.</p>
                <p class="red-warning" style="margin:1.5mm 0 0 0;">NAO COMERCIALIZAMOS COTAS CONTEMPLADAS.</p>
            </div>

            {self._sig_vendedor_cliente_html()}

            {self._footer_html(10)}
        </div>
        """

    # ===================== GENERATE =====================

    def generate(self):
        """Gera o PDF completo usando WeasyPrint"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <style>{self._get_css()}</style>
        </head>
        <body>
            {self._page_1_html()}
            {self._page_2_html()}
            {self._page_3_html()}
            {self._page_4_html()}
            {self._page_5_html()}
            {self._page_6_html()}
            {self._page_7_html()}
            {self._page_8_html()}
            {self._page_9_html()}
            {self._page_10_html()}
        </body>
        </html>
        """
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        return pdf_bytes

    def get_filename(self):
        """Retorna nome do arquivo"""
        nome_limpo = (self.cliente.nome or 'cliente').replace(' ', '_')
        return f"contrato_venda_{nome_limpo}_{self.numero_contrato}.pdf"
