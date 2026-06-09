<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pokémon Calculator</title>
    <style>
        .pkmn-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: inherit;
        }
        .pkmn-btn {
            display: block;
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            text-align: left;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            cursor: pointer;
            color: black;
        }
        .pkmn-btn:hover {
            background-color: #e9ecef;
        }
        .pkmn-section {
            display: none;
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        .pkmn-input {
            width: 100%;
            padding: 8px;
            margin: 8px 0;
            border: 1px solid #ced4da;
            border-radius: 4px;
            color: white;
        }
        .pkmn-result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            color: black;
        }
        .pkmn-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .pkmn-table th, .pkmn-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .pkmn-table th {
            background-color: #f8f9fa;
        }
        .back-btn {
            padding: 8px 16px;
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="pkmn-container">
        <h2>Calculadora Pokémon</h2>

        <div id="main-menu">
            <button class="pkmn-btn" onclick="showSection('drop-section')">Chance de Drop por Lucky</button>
            <button class="pkmn-btn" onclick="showSection('balls-section')">Média de Balls</button>
        </div>

        <div id="drop-section" class="pkmn-section">
            <h3>Chance de Drop por Lucky</h3>
            <select id="elixir" class="pkmn-input">
                <option value="2">Sem Elixir</option>
                <option value="1">Com Elixir</option>
            </select>
            <input type="number" id="drop-percent" class="pkmn-input" placeholder="Porcentagem de Drop (ex: 2.5)" step="0.01" min="0">
            <button class="pkmn-btn" onclick="calculateDrop()">Calcular</button>
            <div id="drop-result" class="pkmn-result"></div>
        </div>

        <div id="balls-section" class="pkmn-section">
            <h3>Média de Balls</h3>
            <input type="number" id="poke-price" class="pkmn-input" placeholder="Preço NPC do Pokémon (ex: 5000)" min="0">
            <input type="number" id="elemental-price" class="pkmn-input" placeholder="Preço da Ball Elemental (ex: 1000)" min="0">
            <button class="pkmn-btn" onclick="calculateBalls()">Calcular</button>
            <div id="balls-result" class="pkmn-result"></div>
        </div>

        <button id="back-button" class="back-btn" onclick="showMainMenu()" style="display: none;">Voltar ao Menu</button>
    </div>

    <script>
        function showSection(sectionId) {
            document.querySelectorAll('.pkmn-section').forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById(sectionId).style.display = 'block';
            document.getElementById('main-menu').style.display = 'none';
            document.getElementById('back-button').style.display = 'block';
        }

        function showMainMenu() {
            document.querySelectorAll('.pkmn-section').forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById('main-menu').style.display = 'block';
            document.getElementById('back-button').style.display = 'none';
        }

        function closeApp() {
            alert('Aplicação encerrada. Obrigado!');
        }

        function calculateDrop() {
            const elixir = document.getElementById('elixir').value;
            const dropPercent = parseFloat(document.getElementById('drop-percent').value);

            if (isNaN(dropPercent) || dropPercent <= 0) {
                alert('Por favor, insira uma porcentagem de drop válida.');
                return;
            }

            const luckys = [0.1, 0.2, 0.35, 0.5, 0.8, 1.0, 1.5];
            const elixir_p = 0.2;
            const elixir_g = 0.8;

            let resultHTML = '<h4>Resultados:</h4>';
            resultHTML += '<table class="pkmn-table">';
            resultHTML += '<tr><th>Lucky</th><th>Drop Rate</th>';

            if (elixir === '1') {
                resultHTML += '<th>+20% Elixir</th><th>+80% Elixir</th>';
            }

            resultHTML += '</tr>';

            for (let l = 0; l < luckys.length; l++) {
                const mult = luckys[l];
                resultHTML += `<tr><td>Lucky ${l+1}</td>`;
                resultHTML += `<td>${(dropPercent * (1 + mult)).toFixed(2)}%</td>`;

                if (elixir === '1') {
                    resultHTML += `<td>${(dropPercent * (1 + mult + elixir_p)).toFixed(2)}%</td>`;
                    resultHTML += `<td>${(dropPercent * (1 + mult + elixir_g)).toFixed(2)}%</td>`;
                }

                resultHTML += '</tr>';
            }

            resultHTML += '</table>';

            const resultDiv = document.getElementById('drop-result');
            resultDiv.innerHTML = resultHTML;
        }

        function calculateBalls() {
            const pokePrice = parseInt(document.getElementById('poke-price').value);
            const elementalPrice = parseInt(document.getElementById('elemental-price').value);

            if (isNaN(pokePrice) || pokePrice <= 0 || isNaN(elementalPrice) || elementalPrice <= 0) {
                alert('Por favor, insira preços válidos.');
                return;
            }

            const elemental = 250;
            const ub = 130;

            const media_elemental = 2 * (pokePrice / elemental);
            const media_ub = 2 * (pokePrice / ub);

            const cost_elemental = Math.ceil((media_elemental * elementalPrice) / 1000);
            const cost_ub = Math.ceil((media_ub * ub) / 1000);

            let resultHTML = '<h4>Resultados:</h4>';
            resultHTML += `<p>Você precisará de aproximadamente <strong>${Math.ceil(media_ub)}</strong> UB/PB `;
            resultHTML += `(<strong>$${cost_ub}k</strong>) ou <strong>${Math.ceil(media_elemental)}</strong> `;
            resultHTML += `Balls Elementais (<strong>$${cost_elemental}k</strong>)</p>`;

            const resultDiv = document.getElementById('balls-result');
            resultDiv.innerHTML = resultHTML;
        }
    </script>
</body>
</html>
