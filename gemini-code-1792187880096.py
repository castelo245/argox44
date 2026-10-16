import zipfile
import os

# Create directory structure
base_dir = "sistema-impressao-argox"
public_dir = os.path.join(base_dir, "public")
os.makedirs(public_dir, exist_ok=True)

# 1. package.json
package_json = """{
  "name": "sistema-impressao-argox",
  "version": "1.0.0",
  "description": "Sistema de Impressão de Etiquetas para Argox OS-214 Plus (100x50mm)",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "cors": "^2.8.5",
    "express": "^4.19.2"
  }
}
"""

# 2. server.js
server_js = """const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Função para remover acentos e caracteres especiais para impressoras térmicas
function normalizarTexto(str) {
  if (!str) return '';
  return str
    .normalize('NFD')
    .replace(/[\\u0300-\\u036f]/g, '')
    .toUpperCase();
}

// Gerador de PPLB (EPL2) para etiqueta 100x50mm (800x400 dots @ 203 DPI)
function gerarPPLB(dados) {
  const produto = normalizarTexto(dados.produto || 'PRODUTO');
  const peso = normalizarTexto(dados.peso || 'PESO LIQ. 600 g');
  const fab = dados.fabricacao || '';
  const val = dados.validade || '';
  const lote = normalizarTexto(dados.lote || 'L-01');
  const conservacao = normalizarTexto(dados.conservacao || 'CONSERVAR A -18 C OU MAIS FRIO');
  const ean = (dados.ean || '7898901234567').replace(/\\D/g, '');
  const alergicos = normalizarTexto(dados.alergicos || 'ALERGICOS: CONTEM DERIVADOS');
  const alergicos2 = normalizarTexto(dados.alergicos2 || 'DE TRIGO E LEITE. CONTEM GLUTEN.');
  const rodapéEsq1 = normalizarTexto(dados.rodapeEsq1 || 'INDUSTRIA BRASILEIRA');
  const rodapéEsq2 = normalizarTexto(dados.rodapeEsq2 || 'SAC: CONTATO@EMPRESA.COM.BR');
  const copias = parseInt(dados.copias, 10) || 1;
  const darkness = parseInt(dados.darkness, 10) || 10;

  // Informações Nutricionais
  const nut = dados.nutricional || {};
  const porcaoTexto = normalizarTexto(nut.porcaoTexto || 'Porcoes por emb.: aprox. 2 | Porcao: 300g');
  const vEnerg100 = nut.vEnerg100 || '180';
  const vEnergPorc = nut.vEnergPorc || '540';
  const vEnergVd = nut.vEnergVd || '27%';

  const carb100 = nut.carb100 || '18';
  const carbPorc = nut.carbPorc || '54';
  const carbVd = nut.carbVd || '18%';

  const prot100 = nut.prot100 || '10';
  const protPorc = nut.protPorc || '30';
  const protVd = nut.protVd || '60%';

  const gord100 = nut.gord100 || '7,5';
  const gordPorc = nut.gordPorc || '22,5';
  const gordVd = nut.gordVd || '35%';

  const sod100 = nut.sod100 || '320';
  const sodPorc = nut.sodPorc || '960';
  const sodVd = nut.sodVd || '48%';

  return [
    'N',
    'q800',
    'Q400,24',
    `D${darkness}`,
    'ZT',
    `; LADO ESQUERDO`,
    `A30,18,0,4,1,1,N,"${produto}"`,
    `A30,52,0,3,1,1,N,"${peso}"`,
    `A30,88,0,2,1,1,N,"FAB: ${fab}   VAL: ${val}"`,
    `A30,112,0,2,1,1,N,"LOTE: ${lote}"`,
    `A30,138,0,1,1,1,N,"${conservacao}"`,
    `B40,180,0,E30,2,4,60,B,"${ean}"`,
    `A30,270,0,1,1,1,N,"${rodapéEsq1}"`,
    `A30,290,0,1,1,1,N,"${rodapéEsq2}"`,
    `; LADO DIREITO - TABELA NUTRICIONAL`,
    `X415,15,2,785,255`,
    `A435,22,0,2,1,1,N,"INFORMACAO NUTRICIONAL"`,
    `LO415,44,370,2`,
    `A425,49,0,1,1,1,N,"${porcaoTexto}"`,
    `LO415,67,370,2`,
    `A425,72,0,1,1,1,N,"Nutriente"`,
    `A575,72,0,1,1,1,N,"100g"`,
    `A645,72,0,1,1,1,N,"300g"`,
    `A720,72,0,1,1,1,N,"%VD*"`,
    `LO415,90,370,1`,
    `A425,96,0,1,1,1,N,"Valor energ. (kcal)"`,
    `A575,96,0,1,1,1,N,"${vEnerg100}"`,
    `A645,96,0,1,1,1,N,"${vEnergPorc}"`,
    `A725,96,0,1,1,1,N,"${vEnergVd}"`,
    `LO415,114,370,1`,
    `A425,120,0,1,1,1,N,"Carboidratos (g)"`,
    `A580,120,0,1,1,1,N,"${carb100}"`,
    `A650,120,0,1,1,1,N,"${carbPorc}"`,
    `A725,120,0,1,1,1,N,"${carbVd}"`,
    `LO415,138,370,1`,
    `A425,144,0,1,1,1,N,"Proteinas (g)"`,
    `A580,144,0,1,1,1,N,"${prot100}"`,
    `A650,144,0,1,1,1,N,"${protPorc}"`,
    `A725,144,0,1,1,1,N,"${protVd}"`,
    `LO415,162,370,1`,
    `A425,168,0,1,1,1,N,"Gorduras tot. (g)"`,
    `A580,168,0,1,1,1,N,"${gord100}"`,
    `A645,168,0,1,1,1,N,"${gordPorc}"`,
    `A725,168,0,1,1,1,N,"${gordVd}"`,
    `LO415,186,370,1`,
    `A425,192,0,1,1,1,N,"Sodio (mg)"`,
    `A575,192,0,1,1,1,N,"${sod100}"`,
    `A645,192,0,1,1,1,N,"${sodPorc}"`,
    `A725,192,0,1,1,1,N,"${sodVd}"`,
    `LO415,210,370,1`,
    `A425,218,0,1,1,1,N,"*Valores Diarios com base em 2000 kcal."`,
    `A415,270,0,1,1,1,N,"${alergicos}"`,
    `A415,290,0,1,1,1,N,"${alergicos2}"`,
    `P${copias}`,
    ''
  ].join('\\r\\n');
}

// Gerador de PPLA para etiqueta 100x50mm
function gerarPPLA(dados) {
  const produto = normalizarTexto(dados.produto || 'PRODUTO');
  const peso = normalizarTexto(dados.peso || 'PESO LIQ. 600 g');
  const fab = dados.fabricacao || '';
  const val = dados.validade || '';
  const lote = normalizarTexto(dados.lote || 'L-01');
  const conservacao = normalizarTexto(dados.conservacao || 'CONSERVAR A -18 C OU MAIS FRIO');
  const ean = (dados.ean || '7898901234567').replace(/\\D/g, '');
  const copias = String(parseInt(dados.copias, 10) || 1).padStart(4, '0');
  const darkness = parseInt(dados.darkness, 10) || 10;

  return [
    '\\x02L',
    'D11',
    `H${darkness}`,
    `131100000180030${produto}`,
    `121100000520030${peso}`,
    `111100000880030FAB: ${fab}   VAL: ${val}`,
    `111100001120030LOTE: ${lote}`,
    `101100001380030${conservacao}`,
    `1F2306001800040${ean}`,
    `101100002700030INDUSTRIA BRASILEIRA`,
    `101100002900030SAC: CONTATO@EMPRESA.COM.BR`,
    `1X1100000150415B02400370002002`,
    `111100000220435INFORMACAO NUTRICIONAL`,
    `1X1100000440415L0370002`,
    `101100000490425Porcoes por emb.: aprox. 2 | Porcao: 300g`,
    `1X1100000670415L0370002`,
    `101100000720425Nutriente`,
    `101100000720575100g`,
    `101100000720645300g`,
    `101100000720720%VD*`,
    `1X1100000900415L0370001`,
    `101100000960425Valor energ. (kcal)`,
    `101100000960575180`,
    `101100000960645540`,
    `10110000096072527%`,
    `1X1100001140415L0370001`,
    `101100001200425Carboidratos (g)`,
    `10110000120058018`,
    `10110000120065054`,
    `10110000120072518%`,
    `1X1100001380415L0370001`,
    `101100001440425Proteinas (g)`,
    `10110000144058010`,
    `10110000144065030`,
    `10110000144072560%`,
    `1X1100001620415L0370001`,
    `101100001680425Gorduras tot. (g)`,
    `1011000016805807,5`,
    `10110000168064522,5`,
    `10110000168072535%`,
    `1X1100001860415L0370001`,
    `101100001920425Sodio (mg)`,
    `101100001920575320`,
    `101100001920645960`,
    `10110000192072548%`,
    `1X1100002100415L0370001`,
    `101100002180425*Valores Diarios com base em 2000 kcal.`,
    `101100002700415ALERGICOS: CONTEM DERIVADOS`,
    `101100002900415DE TRIGO E LEITE. CONTEM GLUTEN.`,
    `Q${copias}`,
    'E',
    ''
  ].join('\\r\\n').replace(/\\\\x02/g, '\\x02');
}

// Rota de status / health check
app.get('/api/status', (req, res) => {
  res.json({ status: 'online', porta: PORT });
});

// Rota para baixar o arquivo PRN bruto
app.post('/api/gerar-prn', (req, res) => {
  const dados = req.body;
  const linguagem = (dados.linguagem || 'PPLB').toUpperCase();
  const conteudo = linguagem === 'PPLA' ? gerarPPLA(dados) : gerarPPLB(dados);

  res.setHeader('Content-disposition', `attachment; filename=etiqueta_${linguagem}.prn`);
  res.setHeader('Content-type', 'application/octet-stream');
  res.send(conteudo);
});

// Rota principal de impressão direta na fila do Windows
app.post('/api/imprimir', (req, res) => {
  const dados = req.body;
  const impressora = dados.nomeImpressora || 'Argox';
  const linguagem = (dados.linguagem || 'PPLB').toUpperCase();
  const payload = linguagem === 'PPLA' ? gerarPPLA(dados) : gerarPPLB(dados);

  const tempFile = path.join(__dirname, `temp_label_${Date.now()}.prn`);

  fs.writeFile(tempFile, payload, 'latin1', (errWrite) => {
    if (errWrite) {
      console.error('Erro ao escrever arquivo temporário:', errWrite);
      return res.status(500).json({ sucesso: false, erro: 'Falha ao gerar arquivo de impressão.' });
    }

    // Envio raw via spooler compartilhado do Windows
    const comando = `cmd /c copy /b "${tempFile}" "\\\\\\\\localhost\\\\${impressora}"`;

    exec(comando, (errExec, stdout, stderr) => {
      // Remove arquivo temporário após envio
      fs.unlink(tempFile, () => {});

      if (errExec) {
        console.error('Erro de execução do spooler:', stderr || errExec.message);
        return res.status(500).json({
          sucesso: false,
          erro: `Falha ao enviar para \\\\\\\\localhost\\\\${impressora}. Verifique se a impressora está compartilhada no Windows com o nome correto.`,
          detalhes: stderr || errExec.message
        });
      }

      console.log(`Etiqueta enviada com sucesso para ${impressora}`);
      return res.json({
        sucesso: true,
        mensagem: `Impressão enviada com sucesso para a impressora [${impressora}]!`,
        copias: dados.copias || 1
      });
    });
  });
});

app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(` Sistema de Impressão Argox OS-214 Plus Ativo!`);
  console.log(` Abra no navegador: http://localhost:${PORT}`);
  console.log(`=======================================================`);
});
"""

# 3. public/index.html
index_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sistema de Impressão Argox OS-214 Plus</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Libre+Barcode+EAN13+Text&display=swap" rel="stylesheet">
</head>
<body>
  <header class="header">
    <div class="logo-area">
      <div class="printer-icon">🖨️</div>
      <div>
        <h1>Argox Print Pro</h1>
        <p>Sistema de Impressão Térmica Direta (OS-214 Plus | 100x50 mm)</p>
      </div>
    </div>
    <div class="status-badge" id="server-status">
      <span class="status-dot"></span>
      <span id="status-text">Conectando ao servidor...</span>
    </div>
  </header>

  <main class="main-container">
    <!-- COLUNA ESQUERDA: FORMULÁRIO -->
    <section class="form-section">
      <div class="card">
        <div class="card-header">
          <h2>📦 Dados do Produto</h2>
          <div class="presets">
            <span>Presets rápidos:</span>
            <button type="button" class="btn-chip" onclick="aplicarPreset('bolonhesa')">Lasanha Bolonhesa 600g</button>
            <button type="button" class="btn-chip" onclick="aplicarPreset('queijos')">Lasanha 4 Queijos 600g</button>
            <button type="button" class="btn-chip" onclick="aplicarPreset('frango')">Lasanha Frango 600g</button>
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label for="produto">Nome do Produto</label>
            <input type="text" id="produto" value="LASANHA BOLONHESA" placeholder="Ex: LASANHA BOLONHESA">
          </div>

          <div class="form-group">
            <label for="peso">Peso Líquido</label>
            <input type="text" id="peso" value="PESO LIQ. 600 g" placeholder="Ex: PESO LIQ. 600 g">
          </div>

          <div class="form-group">
            <label for="lote">Lote</label>
            <input type="text" id="lote" value="L2610-1" placeholder="Ex: L2610-1">
          </div>

          <div class="form-group">
            <label for="fabricacao">Data de Fabricação</label>
            <input type="text" id="fabricacao" value="16/10/2026" placeholder="DD/MM/AAAA">
          </div>

          <div class="form-group">
            <label for="validade">Data de Validade</label>
            <input type="text" id="validade" value="16/04/2027" placeholder="DD/MM/AAAA">
          </div>

          <div class="form-group full-width">
            <label for="conservacao">Condição de Conservação</label>
            <input type="text" id="conservacao" value="CONSERVAR A -18 C OU MAIS FRIO">
          </div>

          <div class="form-group full-width">
            <label for="ean">Código de Barras EAN-13 (13 dígitos numéricos)</label>
            <div class="input-with-button">
              <input type="text" id="ean" maxlength="13" value="7898901234567" placeholder="7898901234567">
              <button type="button" class="btn-secundario" onclick="gerarEanAleatorio()">Gerar EAN</button>
            </div>
            <small id="ean-validation-msg" class="val-ok">✓ Código EAN-13 Válido</small>
          </div>

          <div class="form-group full-width">
            <label for="alergicos">Alérgenos - Linha 1</label>
            <input type="text" id="alergicos" value="ALERGICOS: CONTEM DERIVADOS">
          </div>

          <div class="form-group full-width">
            <label for="alergicos2">Alérgenos - Linha 2</label>
            <input type="text" id="alergicos2" value="DE TRIGO E LEITE. CONTEM GLUTEN.">
          </div>
        </div>
      </div>

      <!-- TABELA NUTRICIONAL -->
      <div class="card">
        <div class="card-header">
          <h2>🥗 Informação Nutricional Reduzida</h2>
        </div>
        <div class="form-grid">
          <div class="form-group full-width">
            <label for="porcaoTexto">Texto de Porções</label>
            <input type="text" id="porcaoTexto" value="Porcoes por emb.: aprox. 2 | Porcao: 300g">
          </div>

          <!-- Tabela Dinâmica -->
          <div class="nutri-table-inputs full-width">
            <table>
              <thead>
                <tr>
                  <th>Nutriente</th>
                  <th>100 g</th>
                  <th>300 g</th>
                  <th>%VD*</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Valor Energético (kcal)</td>
                  <td><input type="text" id="vEnerg100" value="180"></td>
                  <td><input type="text" id="vEnergPorc" value="540"></td>
                  <td><input type="text" id="vEnergVd" value="27%"></td>
                </tr>
                <tr>
                  <td>Carboidratos (g)</td>
                  <td><input type="text" id="carb100" value="18"></td>
                  <td><input type="text" id="carbPorc" value="54"></td>
                  <td><input type="text" id="carbVd" value="18%"></td>
                </tr>
                <tr>
                  <td>Proteínas (g)</td>
                  <td><input type="text" id="prot100" value="10"></td>
                  <td><input type="text" id="protPorc" value="30"></td>
                  <td><input type="text" id="protVd" value="60%"></td>
                </tr>
                <tr>
                  <td>Gorduras Totais (g)</td>
                  <td><input type="text" id="gord100" value="7,5"></td>
                  <td><input type="text" id="gordPorc" value="22,5"></td>
                  <td><input type="text" id="gordVd" value="35%"></td>
                </tr>
                <tr>
                  <td>Sódio (mg)</td>
                  <td><input type="text" id="sod100" value="320"></td>
                  <td><input type="text" id="sodPorc" value="960"></td>
                  <td><input type="text" id="sodVd" value="48%"></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- CONFIGURAÇÃO DA IMPRESSORA -->
      <div class="card">
        <div class="card-header">
          <h2>⚙️ Configuração da Impressora</h2>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label for="nomeImpressora">Nome Compartilhado no Windows</label>
            <input type="text" id="nomeImpressora" value="Argox" placeholder="Ex: Argox">
            <small>Definido em Propriedades da Impressora &gt; Compartilhamento</small>
          </div>

          <div class="form-group">
            <label for="linguagem">Linguagem</label>
            <select id="linguagem">
              <option value="PPLB" selected>PPLB (Emulação EPL2 - Recomendado)</option>
              <option value="PPLA">PPLA (Nativo Argox STX)</option>
            </select>
          </div>

          <div class="form-group">
            <label for="copias">Número de Cópias</label>
            <input type="number" id="copias" min="1" max="100" value="1">
          </div>

          <div class="form-group">
            <label for="darkness">Temperatura / Escurecimento (Darkness)</label>
            <select id="darkness">
              <option value="8">8 - Mais claro</option>
              <option value="10" selected>10 - Padrão Ideal</option>
              <option value="12">12 - Forte</option>
              <option value="14">14 - Extra Escuro (Filmes/Ribbon)</option>
            </select>
          </div>
        </div>
      </div>
    </section>

    <!-- COLUNA DIREITA: PREVIEW E AÇÕES -->
    <section class="preview-section">
      <div class="sticky-card card">
        <div class="card-header">
          <h2>👁️ Pré-visualização da Etiqueta (100 × 50 mm)</h2>
          <span class="dpi-badge">203 DPI (800×400 dots)</span>
        </div>

        <!-- SIMULADOR DA ETIQUETA REAL -->
        <div class="label-wrapper">
          <div class="label-preview" id="label-preview">
            <!-- Coluna Esquerda -->
            <div class="preview-col-left">
              <div class="prev-title" id="prev-produto">LASANHA BOLONHESA</div>
              <div class="prev-subtitle" id="prev-peso">PESO LIQ. 600 g</div>

              <div class="prev-datas">
                <span id="prev-datas-text">FAB: 16/10/2026   VAL: 16/04/2027</span>
                <span id="prev-lote">LOTE: L2610-1</span>
              </div>
              <div class="prev-conservacao" id="prev-conservacao">CONSERVAR A -18 C OU MAIS FRIO</div>

              <div class="prev-barcode-container">
                <div class="simulated-barcode" id="prev-barcode-bars"></div>
                <div class="barcode-digits" id="prev-ean-digits">7 898901 234567</div>
              </div>

              <div class="prev-footer-left">
                <div>INDUSTRIA BRASILEIRA</div>
                <div>SAC: CONTATO@EMPRESA.COM.BR</div>
              </div>
            </div>

            <!-- Coluna Direita -->
            <div class="preview-col-right">
              <div class="nutrition-box">
                <div class="nutri-header">INFORMACAO NUTRICIONAL</div>
                <div class="nutri-portion" id="prev-portion">Porcoes por emb.: aprox. 2 | Porcao: 300g</div>
                <div class="nutri-cols">
                  <span class="c-nut">Nutriente</span>
                  <span class="c-100">100g</span>
                  <span class="c-porc">300g</span>
                  <span class="c-vd">%VD*</span>
                </div>
                <div class="nutri-row">
                  <span class="c-nut">Valor energ. (kcal)</span>
                  <span class="c-100" id="prev-vEnerg100">180</span>
                  <span class="c-porc" id="prev-vEnergPorc">540</span>
                  <span class="c-vd" id="prev-vEnergVd">27%</span>
                </div>
                <div class="nutri-row">
                  <span class="c-nut">Carboidratos (g)</span>
                  <span class="c-100" id="prev-carb100">18</span>
                  <span class="c-porc" id="prev-carbPorc">54</span>
                  <span class="c-vd" id="prev-carbVd">18%</span>
                </div>
                <div class="nutri-row">
                  <span class="c-nut">Proteinas (g)</span>
                  <span class="c-100" id="prev-prot100">10</span>
                  <span class="c-porc" id="prev-protPorc">30</span>
                  <span class="c-vd" id="prev-protVd">60%</span>
                </div>
                <div class="nutri-row">
                  <span class="c-nut">Gorduras tot. (g)</span>
                  <span class="c-100" id="prev-gord100">7,5</span>
                  <span class="c-porc" id="prev-gordPorc">22,5</span>
                  <span class="c-vd" id="prev-gordVd">35%</span>
                </div>
                <div class="nutri-row">
                  <span class="c-nut">Sodio (mg)</span>
                  <span class="c-100" id="prev-sod100">320</span>
                  <span class="c-porc" id="prev-sodPorc">960</span>
                  <span class="c-vd" id="prev-sodVd">48%</span>
                </div>
                <div class="nutri-obs">*Valores Diarios com base em 2000 kcal.</div>
              </div>

              <div class="prev-allergens">
                <div id="prev-alerg1">ALERGICOS: CONTEM DERIVADOS</div>
                <div id="prev-alerg2">DE TRIGO E LEITE. CONTEM GLUTEN.</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AÇÕES -->
        <div class="actions-area">
          <button type="button" class="btn-primary" id="btn-imprimir" onclick="dispararImpressao()">
            <span class="btn-icon">🖨️</span>
            IMPRIMIR NA ARGOX
          </button>
          <button type="button" class="btn-secundario" onclick="baixarArquivoPrn()">
            💾 Baixar Arquivo .PRN (Teste)
          </button>
        </div>

        <div id="feedback-msg" class="feedback-msg"></div>
      </div>
    </section>
  </main>

  <script src="app.js"></script>
</body>
</html>
"""

# 4. public/style.css
style_css = """* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background-color: #0f172a;
  color: #f1f5f9;
  line-height: 1.5;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #334155;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 14px;
}

.printer-icon {
  font-size: 2.2rem;
  background: #1e293b;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #475569;
}

.header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #38bdf8;
}

.header p {
  font-size: 0.85rem;
  color: #94a3b8;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #1e293b;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid #334155;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #eab308;
}

.status-badge.online .status-dot {
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.status-badge.offline .status-dot {
  background: #ef4444;
}

/* LAYOUT PRINCIPAL */
.main-container {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 24px;
  align-items: start;
}

@media (max-width: 1080px) {
  .main-container {
    grid-template-columns: 1fr;
  }
}

.card {
  background: #1e293b;
  border-radius: 12px;
  border: 1px solid #334155;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
  border-bottom: 1px solid #334155;
  padding-bottom: 12px;
}

.card-header h2 {
  font-size: 1.15rem;
  font-weight: 600;
  color: #e2e8f0;
}

.presets {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: #94a3b8;
}

.btn-chip {
  background: #334155;
  color: #cbd5e1;
  border: none;
  padding: 4px 10px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s;
}

.btn-chip:hover {
  background: #0284c7;
  color: #ffffff;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.full-width {
  grid-column: 1 / -1;
}

label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #cbd5e1;
}

input, select {
  background: #0f172a;
  border: 1px solid #475569;
  color: #f8fafc;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

input:focus, select:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

small {
  font-size: 0.75rem;
  color: #94a3b8;
}

.val-ok {
  color: #4ade80 !important;
}

.val-err {
  color: #f87171 !important;
}

.input-with-button {
  display: flex;
  gap: 8px;
}

.input-with-button input {
  flex: 1;
}

/* TABELA NUTRICIONAL DE ENTRADA */
.nutri-table-inputs table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.nutri-table-inputs th, .nutri-table-inputs td {
  padding: 6px 8px;
  border-bottom: 1px solid #334155;
  text-align: left;
}

.nutri-table-inputs th {
  color: #94a3b8;
  font-weight: 600;
}

.nutri-table-inputs td input {
  width: 80px;
  padding: 4px 6px;
  font-size: 0.85rem;
}

/* COLUNA DA PRÉ-VISUALIZAÇÃO */
.sticky-card {
  position: sticky;
  top: 20px;
}

.dpi-badge {
  background: #0369a1;
  color: #e0f2fe;
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.label-wrapper {
  background: #475569;
  padding: 16px;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

/* ETIQUETA REAL (100x50 mm) - Proporção exata 2:1 */
.label-preview {
  width: 520px;
  height: 260px;
  background: #ffffff;
  color: #000000;
  border-radius: 4px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  padding: 12px 14px;
  gap: 12px;
  font-family: 'Arial', sans-serif;
  user-select: none;
  position: relative;
  overflow: hidden;
}

/* Lado Esquerdo */
.preview-col-left {
  display: flex;
  flex-direction: column;
}

.prev-title {
  font-size: 0.92rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.2px;
  line-height: 1.1;
  margin-bottom: 3px;
}

.prev-subtitle {
  font-size: 0.8rem;
  font-weight: 800;
  margin-bottom: 6px;
}

.prev-datas {
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.prev-conservacao {
  font-size: 0.58rem;
  font-weight: 700;
  margin-top: 4px;
  margin-bottom: 8px;
}

/* Código de barras simulado com linhas reais */
.prev-barcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: auto;
  margin-bottom: 6px;
}

.simulated-barcode {
  height: 48px;
  width: 170px;
  background: repeating-linear-gradient(
    90deg,
    #000 0px, #000 2px,
    #fff 2px, #fff 4px,
    #000 4px, #000 5px,
    #fff 5px, #fff 8px,
    #000 8px, #000 11px,
    #fff 11px, #fff 13px,
    #000 13px, #000 14px,
    #fff 14px, #fff 16px,
    #000 16px, #000 18px,
    #fff 18px, #fff 21px
  );
}

.barcode-digits {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.72rem;
  font-weight: bold;
  letter-spacing: 2px;
  margin-top: 2px;
}

.prev-footer-left {
  font-size: 0.52rem;
  font-weight: 600;
  color: #222;
  line-height: 1.2;
}

/* Lado Direito - Tabela Nutricional */
.preview-col-right {
  display: flex;
  flex-direction: column;
}

.nutrition-box {
  border: 1.5px solid #000000;
  padding: 4px 6px;
  font-size: 0.56rem;
  line-height: 1.2;
}

.nutri-header {
  font-weight: 900;
  text-align: center;
  border-bottom: 1.5px solid #000000;
  padding-bottom: 2px;
  font-size: 0.62rem;
}

.nutri-portion {
  font-size: 0.52rem;
  border-bottom: 1.5px solid #000000;
  padding: 2px 0;
  font-weight: 600;
}

.nutri-cols {
  display: flex;
  font-weight: 800;
  border-bottom: 1px solid #000000;
  padding: 2px 0;
}

.nutri-row {
  display: flex;
  border-bottom: 1px dotted #888;
  padding: 1.5px 0;
  font-size: 0.53rem;
}

.nutri-row:last-of-type {
  border-bottom: 1.5px solid #000000;
}

.c-nut { flex: 1.6; font-weight: 600; }
.c-100 { flex: 0.8; text-align: right; }
.c-porc { flex: 0.8; text-align: right; }
.c-vd { flex: 0.8; text-align: right; font-weight: 700; }

.nutri-obs {
  font-size: 0.48rem;
  margin-top: 2px;
  font-style: italic;
}

.prev-allergens {
  margin-top: 8px;
  font-size: 0.52rem;
  font-weight: 800;
  line-height: 1.25;
}

/* BOTÕES DE AÇÃO */
.actions-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-primary {
  background: #16a34a;
  color: #ffffff;
  border: none;
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.4);
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #15803d;
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(1px);
}

.btn-secundario {
  background: #334155;
  color: #f1f5f9;
  border: 1px solid #475569;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secundario:hover {
  background: #475569;
}

.feedback-msg {
  margin-top: 14px;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.85rem;
  display: none;
}

.feedback-msg.sucesso {
  display: block;
  background: #064e3b;
  color: #a7f3d0;
  border: 1px solid #059669;
}

.feedback-msg.erro {
  display: block;
  background: #7f1d1d;
  color: #fecaca;
  border: 1px solid #dc2626;
}
"""

# 5. public/app.js
app_js = """// Presets de produtos cadastrados
const PRESETS = {
  bolonhesa: {
    produto: "LASANHA BOLONHESA",
    peso: "PESO LIQ. 600 g",
    ean: "7898901234567",
    alergicos: "ALERGICOS: CONTEM DERIVADOS",
    alergicos2: "DE TRIGO E LEITE. CONTEM GLUTEN.",
    vEnerg100: "180", vEnergPorc: "540", vEnergVd: "27%",
    carb100: "18", carbPorc: "54", carbVd: "18%",
    prot100: "10", protPorc: "30", protVd: "60%",
    gord100: "7,5", gordPorc: "22,5", gordVd: "35%",
    sod100: "320", sodPorc: "960", sodVd: "48%"
  },
  queijos: {
    produto: "LASANHA QUATRO QUEIJOS",
    peso: "PESO LIQ. 600 g",
    ean: "7898901234574",
    alergicos: "ALERGICOS: CONTEM DERIVADOS",
    alergicos2: "DE TRIGO, LEITE E SOJA. CONTEM LACTOSE.",
    vEnerg100: "195", vEnergPorc: "585", vEnergVd: "29%",
    carb100: "16", carbPorc: "48", carbVd: "16%",
    prot100: "12", protPorc: "36", protVd: "72%",
    gord100: "9,0", gordPorc: "27,0", gordVd: "42%",
    sod100: "350", sodPorc: "1050", sodVd: "53%"
  },
  frango: {
    produto: "LASANHA FRANGO C/ CATUPIRY",
    peso: "PESO LIQ. 600 g",
    ean: "7898901234581",
    alergicos: "ALERGICOS: CONTEM DERIVADOS",
    alergicos2: "DE TRIGO E LEITE. CONTEM GLUTEN.",
    vEnerg100: "170", vEnergPorc: "510", vEnergVd: "26%",
    carb100: "17", carbPorc: "51", carbVd: "17%",
    prot100: "11", protPorc: "33", protVd: "66%",
    gord100: "6,5", gordPorc: "19,5", gordVd: "30%",
    sod100: "310", sodPorc: "930", sodVd: "47%"
  }
};

// Captura todos os dados dos campos do formulário
function coletarDados() {
  return {
    produto: document.getElementById('produto').value.trim(),
    peso: document.getElementById('peso').value.trim(),
    fabricacao: document.getElementById('fabricacao').value.trim(),
    validade: document.getElementById('validade').value.trim(),
    lote: document.getElementById('lote').value.trim(),
    conservacao: document.getElementById('conservacao').value.trim(),
    ean: document.getElementById('ean').value.trim(),
    alergicos: document.getElementById('alergicos').value.trim(),
    alergicos2: document.getElementById('alergicos2').value.trim(),
    nomeImpressora: document.getElementById('nomeImpressora').value.trim(),
    linguagem: document.getElementById('linguagem').value,
    copias: document.getElementById('copias').value,
    darkness: document.getElementById('darkness').value,
    nutricional: {
      porcaoTexto: document.getElementById('porcaoTexto').value.trim(),
      vEnerg100: document.getElementById('vEnerg100').value.trim(),
      vEnergPorc: document.getElementById('vEnergPorc').value.trim(),
      vEnergVd: document.getElementById('vEnergVd').value.trim(),
      carb100: document.getElementById('carb100').value.trim(),
      carbPorc: document.getElementById('carbPorc').value.trim(),
      carbVd: document.getElementById('carbVd').value.trim(),
      prot100: document.getElementById('prot100').value.trim(),
      protPorc: document.getElementById('protPorc').value.trim(),
      protVd: document.getElementById('protVd').value.trim(),
      gord100: document.getElementById('gord100').value.trim(),
      gordPorc: document.getElementById('gordPorc').value.trim(),
      gordVd: document.getElementById('gordVd').value.trim(),
      sod100: document.getElementById('sod100').value.trim(),
      sodPorc: document.getElementById('sodPorc').value.trim(),
      sodVd: document.getElementById('sodVd').value.trim()
    }
  };
}

// Atualiza a visualização em tempo real na tela
function atualizarPreview() {
  const d = coletarDados();

  document.getElementById('prev-produto').textContent = d.produto.toUpperCase() || 'NOME DO PRODUTO';
  document.getElementById('prev-peso').textContent = d.peso.toUpperCase();
  document.getElementById('prev-datas-text').textContent = `FAB: ${d.fabricacao}   VAL: ${d.validade}`;
  document.getElementById('prev-lote').textContent = `LOTE: ${d.lote.toUpperCase()}`;
  document.getElementById('prev-conservacao').textContent = d.conservacao.toUpperCase();

  // Formata os dígitos do EAN-13 para o padrão legível: 7 898901 234567
  const cleanEan = d.ean.replace(/\\D/g, '');
  if (cleanEan.length === 13) {
    document.getElementById('prev-ean-digits').textContent =
      `${cleanEan[0]} ${cleanEan.substring(1, 7)} ${cleanEan.substring(7, 13)}`;
  } else {
    document.getElementById('prev-ean-digits').textContent = cleanEan || '7 898901 234567';
  }

  // Tabela Nutricional
  document.getElementById('prev-portion').textContent = d.nutricional.porcaoTexto;
  document.getElementById('prev-vEnerg100').textContent = d.nutricional.vEnerg100;
  document.getElementById('prev-vEnergPorc').textContent = d.nutricional.vEnergPorc;
  document.getElementById('prev-vEnergVd').textContent = d.nutricional.vEnergVd;

  document.getElementById('prev-carb100').textContent = d.nutricional.carb100;
  document.getElementById('prev-carbPorc').textContent = d.nutricional.carbPorc;
  document.getElementById('prev-carbVd').textContent = d.nutricional.carbVd;

  document.getElementById('prev-prot100').textContent = d.nutricional.prot100;
  document.getElementById('prev-protPorc').textContent = d.nutricional.protPorc;
  document.getElementById('prev-protVd').textContent = d.nutricional.protVd;

  document.getElementById('prev-gord100').textContent = d.nutricional.gord100;
  document.getElementById('prev-gordPorc').textContent = d.nutricional.gordPorc;
  document.getElementById('prev-gordVd').textContent = d.nutricional.gordVd;

  document.getElementById('prev-sod100').textContent = d.nutricional.sod100;
  document.getElementById('prev-sodPorc').textContent = d.nutricional.sodPorc;
  document.getElementById('prev-sodVd').textContent = d.nutricional.sodVd;

  document.getElementById('prev-alerg1').textContent = d.alergicos.toUpperCase();
  document.getElementById('prev-alerg2').textContent = d.alergicos2.toUpperCase();
}

// Cálculo do dígito verificador EAN-13
function calcularDigitoEan13(prefixo12) {
  let soma = 0;
  for (let i = 0; i < 12; i++) {
    const digito = parseInt(prefixo12[i], 10);
    soma += (i % 2 === 0) ? digito * 1 : digito * 3;
  }
  const resto = soma % 10;
  return resto === 0 ? 0 : 10 - resto;
}

function validarEan(ean) {
  const limpo = ean.replace(/\\D/g, '');
  const msgEl = document.getElementById('ean-validation-msg');
  if (limpo.length !== 13) {
    msgEl.textContent = '⚠️ O código EAN-13 deve conter exatamente 13 dígitos numéricos.';
    msgEl.className = 'val-err';
    return false;
  }
  const esperado = calcularDigitoEan13(limpo.substring(0, 12));
  if (parseInt(limpo[12], 10) !== esperado) {
    msgEl.textContent = `⚠️ Dígito verificador incorreto. Deveria terminar em ${esperado}.`;
    msgEl.className = 'val-err';
    return false;
  }
  msgEl.textContent = '✓ Código EAN-13 Válido';
  msgEl.className = 'val-ok';
  return true;
}

function gerarEanAleatorio() {
  let base = '78989';
  for (let i = 0; i < 7; i++) {
    base += Math.floor(Math.random() * 10);
  }
  const dv = calcularDigitoEan13(base);
  const completo = base + dv;
  document.getElementById('ean').value = completo;
  validarEan(completo);
  atualizarPreview();
}

function aplicarPreset(chave) {
  const p = PRESETS[chave];
  if (!p) return;

  document.getElementById('produto').value = p.produto;
  document.getElementById('peso').value = p.peso;
  document.getElementById('ean').value = p.ean;
  document.getElementById('alergicos').value = p.alergicos;
  document.getElementById('alergicos2').value = p.alergicos2;

  document.getElementById('vEnerg100').value = p.vEnerg100;
  document.getElementById('vEnergPorc').value = p.vEnergPorc;
  document.getElementById('vEnergVd').value = p.vEnergVd;

  document.getElementById('carb100').value = p.carb100;
  document.getElementById('carbPorc').value = p.carbPorc;
  document.getElementById('carbVd').value = p.carbVd;

  document.getElementById('prot100').value = p.prot100;
  document.getElementById('protPorc').value = p.protPorc;
  document.getElementById('protVd').value = p.protVd;

  document.getElementById('gord100').value = p.gord100;
  document.getElementById('gordPorc').value = p.gordPorc;
  document.getElementById('gordVd').value = p.gordVd;

  document.getElementById('sod100').value = p.sod100;
  document.getElementById('sodPorc').value = p.sodPorc;
  document.getElementById('sodVd').value = p.sodVd;

  validarEan(p.ean);
  atualizarPreview();
}

// Disparo de impressão para o backend local
async function dispararImpressao() {
  const dados = coletarDados();
  const feedback = document.getElementById('feedback-msg');
  const btn = document.getElementById('btn-imprimir');

  btn.disabled = true;
  btn.innerHTML = '⏳ Enviando para a Argox...';
  feedback.className = 'feedback-msg';
  feedback.style.display = 'none';

  try {
    const res = await fetch('/api/imprimir', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    const resultado = await res.json();

    if (res.ok && resultado.sucesso) {
      feedback.textContent = `✅ ${resultado.mensagem}`;
      feedback.className = 'feedback-msg sucesso';
    } else {
      feedback.textContent = `❌ ${resultado.erro || 'Falha ao imprimir.'}`;
      feedback.className = 'feedback-msg erro';
    }
  } catch (err) {
    feedback.textContent = `❌ Não foi possível conectar ao servidor local na porta 4000. Certifique-se de que o backend está em execução.`;
    feedback.className = 'feedback-msg erro';
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">🖨️</span> IMPRIMIR NA ARGOX';
  }
}

// Download do arquivo .PRN para testes manuais
async function baixarArquivoPrn() {
  const dados = coletarDados();
  try {
    const res = await fetch('/api/gerar-prn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `etiqueta_${dados.linguagem.toLowerCase()}_100x50.prn`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (e) {
    alert('Erro ao gerar arquivo PRN');
  }
}

// Verificação periódica do status do servidor
async function checarStatusServidor() {
  const badge = document.getElementById('server-status');
  const txt = document.getElementById('status-text');

  try {
    const res = await fetch('/api/status', { method: 'GET' });
    if (res.ok) {
      badge.className = 'status-badge online';
      txt.textContent = 'Servidor de Impressão Online';
      return;
    }
  } catch (err) {}

  badge.className = 'status-badge offline';
  txt.textContent = 'Servidor Local Desconectado (Porta 4000)';
}

// Event Listeners
document.querySelectorAll('input, select').forEach(elem => {
  elem.addEventListener('input', () => {
    if (elem.id === 'ean') validarEan(elem.value);
    atualizarPreview();
  });
});

// Inicialização
checarStatusServidor();
setInterval(checarStatusServidor, 5000);
validarEan(document.getElementById('ean').value);
atualizarPreview();
"""

# 6. iniciar.bat
iniciar_bat = """@echo off
title Sistema de Impressao Argox OS-214 Plus
cls
echo =============================================================
echo   INICIALIZANDO O SISTEMA DE IMPRESSAO ARGOX OS-214 PLUS
echo =============================================================
echo.

IF NOT EXIST node_modules (
    echo [1/3] Instalando dependencias necessarias (Express, Cors)...
    call npm install
) ELSE (
    echo [1/3] Dependencias ja instaladas.
)

echo [2/3] Abrindo interface no navegador padrao...
start http://localhost:4000

echo [3/3] Iniciando o servidor de comunicacao com a impressora...
echo.
node server.js
pause
"""

# 7. README.md
readme_md = """# Sistema de Impressão de Etiquetas Argox OS-214 Plus (100 × 50 mm)

Sistema completo pronto para uso com interface web moderna, pré-visualização em tempo real e envio direto de comandos nativos (**PPLB / PPLA**) para a fila de impressão da **Argox OS-214 Plus** no Windows.

---

## 🚀 Como Iniciar em 1 Minuto

1. Certifique-se de ter o **Node.js** instalado no computador.
2. Dê um duplo-clique no arquivo **`iniciar.bat`**.
3. O script instalará as dependências automaticamente, abrirá o navegador em `http://localhost:4000` e iniciará o serviço de comunicação.

---

## 🖨️ Passo Fundamental: Compartilhar a Impressora no Windows

Para que o servidor consiga despachar os comandos brutos diretamente para a impressora via rede local (`\\\\localhost\\Argox`):

1. No Windows, abra o menu **Executar** (`Win + R`), digite `control printers` e tecle Enter.
2. Clique com o botão direito na **Argox OS-214 Plus** e escolha **Propriedades da Impressora**.
3. Vá na aba **Compartilhamento**.
4. Marque a caixa **Compartilhar esta impressora**.
5. No campo **Nome do compartilhamento**, digite: `Argox` (sem espaços).
6. Clique em **Aplicar** e **OK**.

---

## 📐 Especificações da Etiqueta

* **Dimensão:** 100 mm × 50 mm
* **Resolução:** 203 DPI (800 dots de largura × 400 dots de altura útil)
* **Gap padrão:** 3,0 mm (24 dots)
* **Linguagens Suportadas:** PPLB (Emulação EPL2) e PPLA (Nativo Argox)
* **Código de Barras:** EAN-13 vetorial de alta definição com cálculo automático de dígito verificador.
* **Tabela Nutricional:** Padrão reduzido conforme exigências da ANVISA (100g / porção / %VD).
"""

# Escreve todos os arquivos
files_to_write = {
    os.path.join(base_dir, "package.json"): package_json,
    os.path.join(base_dir, "server.js"): server_js,
    os.path.join(base_dir, "iniciar.bat"): iniciar_bat,
    os.path.join(base_dir, "README.md"): readme_md,
    os.path.join(public_dir, "index.html"): index_html,
    os.path.join(public_dir, "style.css"): style_css,
    os.path.join(public_dir, "app.js"): app_js,
}

for path_file, content in files_to_write.items():
    with open(path_file, "w", encoding="utf-8") as f:
        f.write(content)

# Gera o arquivo zip
zip_filename = "argox-print-system-100x50.zip"
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, start=".")
            zipf.write(full_path, arcname)

print(f"Zip created successfully: {zip_filename}")