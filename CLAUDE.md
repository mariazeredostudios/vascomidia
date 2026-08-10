# Vasco International — memória do projeto

Este arquivo é lido automaticamente pelo Claude Code sempre que uma sessão for
aberta nesta pasta. Ele existe para que o histórico, as regras e os erros já
corrigidos no Cowork não se percam na migração. Leia inteiro antes de agir.

## O que é o projeto

O **Vasco da Gama International** é uma iniciativa da **IE Sports** (empresa
que administra intercâmbios esportivos para diversos clubes brasileiros) em
parceria com a **Vasco da Gama SAF**, para selecionar atletas de **8 a 19
anos** para representar o Vasco em competições internacionais de futebol
amador. A competição em destaque no momento é a **Disney Cup 2027**, em
Orlando (EUA).

A seleção acontece por meio de treinos ministrados por **treinadores da base
do clube** (as "seletivas"), com inscrição paga via Sympla.

Responsável pelo projeto: **Maria Azeredo** (dudsazeredo2014@gmail.com).

## Fatos oficiais — nunca inventar, sempre conferir aqui

- **Data da seletiva:** 16 de agosto de 2026, das 08h às 12h.
- **Faixas de horário:** 08h–10h = nascidos entre 2013 e 2018 · 10h–12h =
  nascidos entre 2007 e 2012.
- **Local:** CT Almirante Heleno de Barros Nunes — Parque Sarapuí, Duque de
  Caxias/RJ.
- **Idade elegível:** 8 a 19 anos.
- **Inscrição oficial (Sympla):**
  sympla.com.br/evento/seletiva-vasco-international/3477937 — **cuidado**:
  existe um evento antigo/encerrado com URL muito parecida
  (.../3101125, de 12/10/2025). Nunca divulgar essa.
- **E-mail de contato:** o post oficial do @vascoacademy tem um erro de
  digitação no e-mail; o correto está confirmado na página do Sympla.

## Identidade visual oficial (Direcional Visual 2026)

- **Fonte principal:** Futura Condensed Extra Bold (títulos/chamadas). Não
  está instalada no ambiente de geração — o fallback local mais fiel é
  **Nimbus Sans Narrow Bold**
  (`/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf`). Não usar
  Poppins Bold para títulos — não é condensada e já foi trocada por isso.
- **Fonte secundária:** Barlow Regular/Bold (textos corridos). Fallback local:
  Poppins Regular/Medium.
- **Paleta:** preto `#0E0E0E`, branco `#F7F7F5`, vermelho da cruz de Malta
  `#C52822` (acento pontual, nunca em blocos grandes), dourado do navio
  `#9C7728` (acento secundário).
- **Recurso gráfico oficial:** corte diagonal preto/branco — é o mesmo padrão
  do próprio escudo do clube e aparece nos "Exemplos de Aplicação" do
  Direcional Visual. Usar isso em vez de fundos escuros uniformes sempre que
  possível — dá muito mais identidade do que gradientes genéricos.
- **Marca d'água:** cruz de Malta vermelha, discreta, geralmente no canto.
- **Fotografia:** sempre priorizar movimento e elementos que "traduzam" o
  Vasco (torcida, jogadores, o Almirante).
- **PDF de referência completo:** `DIRECIONAL_VISUAL_VASCO2026.pdf` e as
  páginas extraídas em `kv_pages/page_1.png` a `page_6.png`.

### Regra de emoji — ATENÇÃO, já corrigida duas vezes

**Nunca usar o emoji ⚫🔴 (bolinha preta + vermelha) em legendas ou textos.**
Maria já pediu para não usar isso mais de uma vez. Evitar também qualquer
combinação decorativa de círculos coloridos como abertura de legenda — vai
direto ao texto ou usa no máximo os emojis numéricos (1️⃣2️⃣3️⃣) quando fizer
sentido para uma lista.

## Contas geridas

| Rede | Handle |
|---|---|
| Instagram | @vasco_international |
| X (Twitter) | (ver perfil atual) |
| Threads | (ver perfil atual) |
| TikTok | @vasco.international |

## Regras de engajamento (rodada diária, por conta)

- **Curtidas:** até 25/dia.
- **Seguir:** até 13/dia. Priorizar **páginas/empresas com 5 mil+
  seguidores** relacionadas ao Vasco — não vale a pena seguir pessoas físicas
  pequenas só porque são vascaínas. Depois de esgotar essas, olhar contas
  menores.
- **Comentários:** até 15/dia (respostas a dúvidas de terceiros não contam
  nesse limite).
- Não há necessidade de dar unfollow em ninguém, nem limite de ações totais
  por dia.
- **Nunca comentar duas vezes no mesmo post** — sempre checar comentários
  existentes (buscar "vasco_international" na página) antes de comentar.
- Quando pertinente, comentários podem mencionar o programa e fazer
  propaganda sutil do produto — **exceto** na regra abaixo.
- **@iesportsbr:** curtir só quando o post for sobre o Vasco. Comentar
  **apenas** para responder dúvida de cliente ou potencial cliente — nunca
  para fazer propaganda do Vasco International em posts sobre outros clientes
  da IE Sports (ex.: seletiva do Bahia). Isso já causou um incidente grave
  corrigido anteriormente.
- "Arquivo Vascaíno" é só compra/venda de camisa — não interagir muito lá.
- Documento antigo `Estrategia_Engajamento_Ativo.md` tem comentários prontos
  que **não devem ser usados literalmente** — só os limites/cadência dele são
  referência, e mesmo isso foi substituído pelos limites acima.
- Janelas ideais de postagem (horário de Brasília): 7h–9h · 12h–13h30 ·
  18h–21h30.

## Pipeline de geração dos reels (faceless, motion graphics)

Scripts em `scripts/`. Dependências: Python 3, `numpy`, `Pillow`, `ffmpeg`
(sem `moviepy` — não está disponível, tudo é feito com PIL + ffmpeg puro).
Sem acesso à internet no ambiente de geração — por isso a trilha sonora é
**sempre sintetizada do zero** (nunca baixar áudio de terceiros).

1. `build_reel3.py` — gera as 7 cenas estáticas (PNG 1080×1920) com PIL,
   usando o sistema de corte diagonal preto/branco descrito acima. É o
   template mais atual e o que deve ser usado como base para os próximos
   reels (trocar textos/conteúdo, manter a estrutura visual).
2. `animate3.py` — aplica zoom Ken Burns (`zoompan` do ffmpeg, alternando
   zoom-in/zoom-out por cena) e transições crossfade (`xfade`) entre as
   cenas, gera o vídeo mudo.
3. `make_music3.py` — sintetiza uma trilha original via `numpy` (kick, hi-hat,
   clap, sub-bass, arpejo, riser e impacto antes do CTA final) e exporta um
   `.wav`. 100% original, sem risco de direito autoral.
4. Mux final: `ffmpeg -i video.mp4 -i musica.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest saida.mp4`
5. Copiar o resultado para a pasta do projeto com a data no nome do arquivo.

`build_reel_v1.py` / `animate_v1.py` / `make_music_v1.py` = template do
primeiro reel (contagem regressiva, fundo escuro uniforme). Mantido só de
referência histórica — **não usar como base para reels novos**, foi
substituído pelo template v3 (corte diagonal) porque o v1/v2 pareciam
repetitivos demais entre si.

`build_reel_v2_deprecated.py` foi a primeira tentativa do reel "5 passos" —
reaproveitava o template v1 quase sem alteração visual e foi rejeitada por
Maria por parecer pobre e repetitiva. Não reaproveitar essa estrutura.

`build_strategy_doc.py` gera `Estrategia_Conteudo_Reta_Final_Seletiva.docx`
(pesquisa de virilidade + calendário de 7 dias + ideias de reels/posts).

`build_pdf.py` gera `Vasco_International_Resumo_do_Projeto.pdf` (resumo
completo do projeto para qualquer pessoa entender e replicar).

## Bug conhecido (ambiente Cowork, pode não existir no Claude Code)

A ferramenta de upload de arquivo do Chrome MCP (`file_upload`) quebra de
forma consistente para qualquer arquivo que realmente exista no disco — erro
`Invalid arguments... paths expected array received undefined`. Arquivos
falsos/inexistentes passam da validação normalmente, o que confirma que é bug
da ferramenta, não do caminho usado. Isso impediu a publicação automática de
vídeos direto pelo navegador durante o uso do Cowork. Se o Claude Code tiver
seu próprio fluxo de automação de navegador (ex.: Playwright), vale testar se
o mesmo problema ocorre lá — é bem possível que não.

## Calendário de conteúdo em andamento (sprint de 7 dias até 16/08)

Ver `Estrategia_Conteudo_Reta_Final_Seletiva.docx` para o plano completo.
Resumo rápido:

| Data | D- | Reel âncora |
|---|---|---|
| 09/08 | D-7 | Contagem regressiva "faltam 7 dias" (publicado) |
| 10/08 | D-6 | "5 passos para participar" (pronto, ver pasta) |
| 11/08 | D-5 | "3 sinais de que uma seletiva é confiável" (a fazer) |
| 12/08 | D-4 | "O que rola na Disney Cup 2027" (a fazer) |
| 13/08 | D-3 | Depoimento/bastidores reais (a fazer, depende de disponibilidade de alguém pra gravar) |
| 14/08 | D-2 | "Mito vs. Verdade" (a fazer) |
| 15/08 | D-1 | Urgência máxima — véspera (a fazer) |
| 16/08 | Dia D | Cobertura ao vivo em Stories no CT (a fazer) |

## Pendências abertas

- Publicar manualmente os reels já prontos (bug de upload, ver acima).
- Organizar Destaques (Highlights) do perfil — bloqueado até Maria postar um
  Story pelo celular.
- Revisar novos arquivos de vídeo que aparecerem na pasta Downloads.
- Continuar rodadas diárias de engajamento dentro dos limites acima.
- Seguir o calendário de conteúdo acima para os dias restantes.

## Assets principais na pasta

- `avatar_vasco_intl.png`, `banner_vasco_intl.png` — identidade das contas.
- `DIRECIONAL_VISUAL_VASCO2026.pdf` + `kv_pages/` — guia de marca oficial.
- `Vasco_International_Resumo_do_Projeto.pdf` — resumo completo do projeto.
- `Estrategia_Conteudo_Reta_Final_Seletiva.docx` — pesquisa + calendário de
  conteúdo + ideias de reels/posts detalhadas.
- `Reel_Contagem_Seletiva_09-08-2026.mp4` — reel D-7, publicado.
- `Reel_5_Passos_Seletiva_10-08-2026.mp4` — reel D-6, pronto para postar.
- `scripts/` — todo o pipeline de geração descrito acima.
