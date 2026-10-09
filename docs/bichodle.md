<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bichodle - O Quiz do Jogo do Bicho</title>
    <!-- Tailwind CSS estável via CDN -->
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        /* CSS Nativo Garantido para a Grade de Atributos */
        .grade-bichodle {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 8px;
            text-align: center;
        }
        .bloco-quadrado {
            aspect-ratio: 1 / 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            padding: 4px;
            font-weight: bold;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        /* Animação de revelação estilo Pokédle */
        .bloco-animado {
            animation: flipIn 0.4s ease forwards;
            opacity: 0;
        }
        @keyframes flipIn {
            0% { transform: rotateX(-90deg); opacity: 0; }
            100% { transform: rotateX(0deg); opacity: 1; }
        }
    </style>
</head>
<body class="bg-stone-950 text-stone-100 min-h-screen flex flex-col items-center p-4">

    <header class="border-b border-stone-800 w-full max-w-2xl text-center py-4 mb-6">
        <h1 class="text-3xl font-black tracking-widest text-emerald-500">BICHODLE</h1>
        <p class="text-xs text-stone-400 font-mono mt-1">PROJETO CULTURAL - ADIVINHE O BICHO E A DEZENA</p>
    </header>

    <main class="w-full max-w-2xl flex-1 flex flex-col items-center">

        <!-- Painel de Inputs -->
        <div class="w-full bg-stone-900 p-4 rounded-2xl border border-stone-800 mb-6 z-50">
            <div class="flex flex-col md:flex-row gap-3">

                <!-- Busca do Animal -->
                <div class="relative flex-1">
                    <input type="text" id="input-busca" placeholder="Digite o bicho (ex: Avestruz)..."
                        class="w-full p-3 bg-stone-800 border-2 border-stone-700 rounded-xl text-stone-100 focus:outline-none focus:border-emerald-500 text-base"
                        autocomplete="off">
                    <!-- Caixa de sugestões flutuante -->
                    <div id="dropdown-sugestoes" class="absolute left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-stone-800 border border-stone-700 rounded-xl hidden shadow-2xl z-50"></div>
                </div>

                <!-- Seletor de Dezena Dinâmico -->
                <div class="w-full md:w-48">
                    <select id="select-dezena" disabled
                        class="w-full p-3 bg-stone-800 border-2 border-stone-700 rounded-xl text-stone-100 focus:outline-none focus:border-emerald-500 text-base disabled:opacity-40 cursor-pointer">
                        <option value="">Escolha o bicho primeiro</option>
                    </select>
                </div>

                <!-- Botão Confirmar -->
                <button id="btn-enviar" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-6 py-3 rounded-xl transition-all cursor-pointer text-base">
                    Enviar
                </button>

            </div>
        </div>

        <!-- Grade de Resultados anteriores -->
        <div class="w-full overflow-x-auto pb-4">
            <div class="min-w-[600px]">
                <!-- Cabeçalho fixo -->
                <div class="grade-bichodle text-xs font-bold text-stone-400 uppercase tracking-wider mb-3 px-1">
                    <div>Animal</div>
                    <div>Sua Dezena</div>
                    <div>Grupo</div>
                    <div>Dezenas Bicho</div>
                    <div>Classe</div>
                    <div>Alimentação</div>
                </div>
                <!-- Onde os palpites vão aparecer empilhados -->
                <div id="grid-palpites" class="flex flex-col gap-2"></div>
            </div>
        </div>
    </main>

    <script>
        // Banco de Dados Oficial Completo com os 25 Animais
        const baseBichos = [
            { nome: "Avestruz", emoji: "🦩", grupo: 1, dezenasArr: [1, 2, 3, 4], dezenasTxt: "01-04", classe: "Ave", dieta: "Onívoro" },
            { nome: "Águia", emoji: "🦅", grupo: 2, dezenasArr: [5, 6, 7, 8], dezenasTxt: "05-08", classe: "Ave", dieta: "Carnívoro" },
            { nome: "Burro", emoji: "🫏", grupo: 3, dezenasArr: [9, 10, 11, 12], dezenasTxt: "09-12", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Borboleta", emoji: "🦋", grupo: 4, dezenasArr: [13, 14, 15, 16], dezenasTxt: "13-16", classe: "Inseto", dieta: "Nectarívoro" },
            { nome: "Cachorro", emoji: "🐶", grupo: 5, dezenasArr: [17, 18, 19, 20], dezenasTxt: "17-20", classe: "Mamífero", dieta: "Carnívoro" },
            { nome: "Cabra", emoji: "🐐", grupo: 6, dezenasArr: [21, 22, 23, 24], dezenasTxt: "21-24", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Carneiro", emoji: "🐏", grupo: 7, dezenasArr: [25, 26, 27, 28], dezenasTxt: "25-28", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Camelo", emoji: "🐪", grupo: 8, dezenasArr: [29, 30, 31, 32], dezenasTxt: "29-32", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Cobra", emoji: "🐍", grupo: 9, dezenasArr: [33, 34, 35, 36], dezenasTxt: "33-36", classe: "Réptil", dieta: "Carnívoro" },
            { nome: "Coelho", emoji: "🐰", grupo: 10, dezenasArr: [37, 38, 39, 40], dezenasTxt: "37-40", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Cavalo", emoji: "🐴", grupo: 11, dezenasArr: [41, 42, 43, 44], dezenasTxt: "41-44", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Elefante", emoji: "🐘", grupo: 12, dezenasArr: [45, 46, 47, 48], dezenasTxt: "45-48", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Galo", emoji: "🐓", grupo: 13, dezenasArr: [49, 50, 51, 52], dezenasTxt: "49-52", classe: "Ave", dieta: "Onívoro" },
            { nome: "Gato", emoji: "🐱", grupo: 14, dezenasArr: [53, 54, 55, 56], dezenasTxt: "53-56", classe: "Mamífero", dieta: "Carnívoro" },
            { nome: "Jacaré", emoji: "🐊", grupo: 15, dezenasArr: [57, 58, 59, 60], dezenasTxt: "57-60", classe: "Réptil", dieta: "Carnívoro" },
            { nome: "Leão", emoji: "🦁", grupo: 16, dezenasArr: [61, 62, 63, 64], dezenasTxt: "61-64", classe: "Mamífero", dieta: "Carnívoro" },
            { nome: "Macaco", emoji: "🐵", grupo: 17, dezenasArr: [65, 66, 67, 68], dezenasTxt: "65-68", classe: "Mamífero", dieta: "Onívoro" },
            { nome: "Porco", emoji: "🐷", grupo: 18, dezenasArr: [69, 70, 71, 72], dezenasTxt: "69-72", classe: "Mamífero", dieta: "Onívoro" },
            { nome: "Pavão", emoji: "🦚", grupo: 19, dezenasArr: [73, 74, 75, 76], dezenasTxt: "73-76", classe: "Ave", dieta: "Onívoro" },
            { nome: "Peru", emoji: "🦃", grupo: 20, dezenasArr: [77, 78, 79, 80], dezenasTxt: "77-80", classe: "Ave", dieta: "Onívoro" },
            { nome: "Touro", emoji: "🐂", grupo: 21, dezenasArr: [81, 82, 83, 84], dezenasTxt: "81-84", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Tigre", emoji: "🐯", grupo: 22, dezenasArr: [85, 86, 87, 88], dezenasTxt: "85-88", classe: "Mamífero", dieta: "Carnívoro" },
            { nome: "Urso", emoji: "🐻", grupo: 23, dezenasArr: [89, 90, 91, 92], dezenasTxt: "89-92", classe: "Mamífero", dieta: "Onívoro" },
            { nome: "Veado", emoji: "🦌", grupo: 24, dezenasArr: [93, 94, 95, 96], dezenasTxt: "93-96", classe: "Mamífero", dieta: "Herbívoro" },
            { nome: "Vaca", emoji: "🐮", grupo: 25, dezenasArr: [97, 98, 99, 0], dezenasTxt: "97-00", classe: "Mamífero", dieta: "Herbívoro" }
        ];

        // Resposta Secreta do Jogo (Exemplo: AVESTRUZ e dezena 03)
        const bichoSecreto = baseBichos.find(b => b.nome === "Avestruz");
        const dezenaSecreta = 3;

        // Seletores JavaScript
        const inputBusca = document.getElementById("input-busca");
        const selectDezena = document.getElementById("select-dezena");
        const dropdown = document.getElementById("dropdown-sugestoes");
        const btnEnviar = document.getElementById("btn-enviar");
        const gridPalpites = document.getElementById("grid-palpites");

        let animalSelecionado = null;

        // Limpeza de texto para buscas sem acentos ou maiúsculas
        function tratarTexto(texto) {
            return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
        }

        // Lógica de Monitoramento da Digitação
        inputBusca.addEventListener("input", () => {
            const digitado = tratarTexto(inputBusca.value);
            dropdown.innerHTML = "";

            if (digitado === "") {
                dropdown.classList.add("hidden");
                bloquearDezenas();
                return;
            }

            // Confere se o usuário já digitou o nome inteiro perfeitamente
            const bichoExato = baseBichos.find(b => tratarTexto(b.nome) === digitado);
            if (bichoExato) {
                definirAnimal(bichoExato);
                dropdown.classList.add("hidden");
                return;
            }

            // Caso contrário, mostra a lista filtrada de sugestões
            const filtrados = baseBichos.filter(b => tratarTexto(b.nome).includes(digitado));

            if (filtrados.length > 0) {
                dropdown.classList.remove("hidden");
                filtrados.forEach(bicho => {
                    const item = document.createElement("div");
                    item.className = "p-3 hover:bg-stone-700 cursor-pointer border-b border-stone-700 last:border-0 flex items-center gap-3 text-stone-200 font-medium";
                    item.innerHTML = `<span class="text-xl">${bicho.emoji}</span><span>${bicho.nome}</span>`;

                    // Evento de clique na opção sugerida
                    item.addEventListener("click", () => {
                        definirAnimal(bicho);
                        dropdown.classList.add("hidden");
                    });
                    dropdown.appendChild(item);
                });
            } else {
                dropdown.classList.add("hidden");
            }
        });

        // Configura o animal escolhido e destrava o seletor de dezenas
        function definirAnimal(bicho) {
            inputBusca.value = bicho.nome;
            animalSelecionado = bicho;

            selectDezena.innerHTML = '<option value="" disabled selected>Escolha a dezena...</option>';
            selectDezena.disabled = false;

            bicho.dezenasArr.forEach(num => {
                const opt = document.createElement("option");
                opt.value = num;
                opt.textContent = num.toString().padStart(2, '0');
                selectDezena.appendChild(opt);
            });
        }

        function bloquearDezenas() {
            animalSelecionado = null;
            selectDezena.innerHTML = '<option value="">Escolha o bicho primeiro</option>';
            selectDezena.disabled = true;
        }

        // Fecha o menu de buscas se o usuário clicar em outra parte da tela
        document.addEventListener("click", (e) => {
            if (!inputBusca.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add("hidden");
            }
        });

        // Evento de Envio do Palpite
        btnEnviar.addEventListener("click", () => {
            const dezenaChotada = selectDezena.value;

            if (!animalSelecionado || dezenaChotada === "") {
                alert("Por favor, digite um animal válido e escolha uma de suas dezenas!");
                return;
            }

            const valorDezena = parseInt(dezenaChotada, 10);
            criarLinhaResultado(animalSelecionado, valorDezena);

            // Reseta para a próxima tentativa
            inputBusca.value = "";
            bloquearDezenas();
        });

        // Cria a linha de quadradinhos estilo Pokédle na tela
        function criarLinhaResultado(palpiteBicho, palpiteDezena) {
            const linha = document.createElement("div");
            linha.className = "grade-bichodle";

            // Mapeia os dados estruturais de verificação
            const colunas = [
                { tipo: 'animal', valor: palpiteBicho.nome, correto: bichoSecreto.nome, extra: palpiteBicho.emoji },
                { tipo: 'dezena', valor: palpiteDezena, correto: dezenaSecreta },
                { tipo: 'grupo', valor: palpiteBicho.grupo, correto: bichoSecreto.grupo },
                { tipo: 'texto', valor: palpiteBicho.dezenasTxt, correto: bichoSecreto.dezenasTxt },
                { tipo: 'texto', valor: palpiteBicho.classe, correto: bichoSecreto.classe },
                { tipo: 'texto', valor: palpiteBicho.dieta, correto: bichoSecreto.dieta }
            ];

            colunas.forEach((col, index) => {
                const bloco = document.createElement("div");
                bloco.className = "bloco-quadrado bloco-animado text-xs md:text-sm";
                bloco.style.animationDelay = `${index * 100}ms`;

                // Validação de acertos por cores
                if (col.valor === col.correto) {
                    bloco.classList.add("bg-emerald-600", "text-white"); // Verde
                } else {
                    bloco.classList.add("bg-rose-700", "text-stone-100"); // Vermelho
                }

                // Personalização do texto dentro de cada quadrado
                if (col.tipo === 'animal') {
                    bloco.innerHTML = `<span class="text-xl mb-1">${col.extra}</span><span class="truncate max-w-full">${col.valor}</span>`;
                }
                else if (col.tipo === 'dezena') {
                    let seta = col.valor < col.correto ? " ⬆️" : " ⬇️";
                    let nFormatado = col.valor.toString().padStart(2, '0');
                    bloco.innerHTML = `<span>${nFormatado}</span><span class="text-[10px] font-normal text-stone-300 mt-1">${col.valor === col.correto ? 'Exato' : seta}</span>`;
                }
                else if (col.tipo === 'grupo') {
                    let seta = col.valor < col.correto ? " ⬆️" : " ⬇️";
                    let gFormatado = col.valor.toString().padStart(2, '0');
                    bloco.innerHTML = `<span>G-${gFormatado}</span><span class="text-[10px] font-normal text-stone-300 mt-0.5">${seta}</span>`;
                }
                else {
                    bloco.innerHTML = `<span class="truncate max-w-full">${col.valor}</span>`;
                }

                linha.appendChild(bloco);
            });

            // Insere sempre no topo do histórico
            gridPalpites.insertBefore(linha, gridPalpites.firstChild);

            // Condição de Vitória Completa
            if (palpiteBicho.nome === bichoSecreto.nome && palpiteDezena === dezenaSecreta) {
                inputBusca.disabled = true;
                selectDezena.disabled = true;
                btnEnviar.disabled = true;
                setTimeout(() => {
                    alert("🎯 DEU NO POSTE! Você decifrou o bicho e a dezena do dia! 🎉");
                }, 700);
            }
        }
    </script>
</body>
</html>
