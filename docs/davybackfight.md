<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random List Splitter</title>
    <style>
        .splitter-container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 1.5rem;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            color: black;
            background-color: #f6f8fa;
        }

        .splitter-title {
            margin-top: 0;
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 0.5rem;
        }

        .input-area {
            width: 100%;
            min-height: 150px;
            padding: 12px;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            box-sizing: border-box;
        }

        .input-area:focus {
            border-color: #0366d6;
            outline: none;
            box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
        }

        .split-button {
            display: block;
            width: 100%;
            padding: 10px 16px;
            margin: 1rem 0;
            background-color: #28a745;
            color: white;
            border: 1px solid rgba(27, 31, 35, 0.15);
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .split-button:hover {
            background-color: #269f42;
        }

        .split-button:active {
            background-color: #279f43;
        }

        .results-container {
            display: flex;
            gap: 20px;
            margin-top: 1.5rem;
        }

        .result-set {
            flex: 1;
            background: white;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            padding: 1rem;
        }

        .result-title {
            margin-top: 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e1e4e8;
            color: #24292e;
            text-align: center;
            background-color: #f1f8ff;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
        }

        .result-list {
            list-style-type: none;

            padding-left: 0;
            margin: 0;
        }

        .result-list li {
            padding: 10px 12px;
            margin-bottom: 10px;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            background-color: #fafbfc;
            box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
            transition: background-color 0.2s;
        }

        .result-list li:hover {
            background-color: #f3f4f6;
        }

        .empty-message {
            color: #6a737d;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }

        .set-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .item-count {
            background-color: #eaf5ff;
            color: #0366d6;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        @media (max-width: 768px) {
            .results-container {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="splitter-container">
        <h2 class="splitter-title">Davy Back Fight</h2>

        <textarea class="input-area" id="listInput" placeholder="Enter the name of everyone available in both crews, one per line. For example:
Usopp
Sanji
Katakuri
Smoothie"></textarea>

        <button class="split-button" id="splitBtn">Split List Randomly</button>

        <div class="results-container">
            <div class="result-set">
                <div class="set-header">
                    <span id="count1" class="item-count">0 pirates</span>
                </div>
                <ul id="set1" class="result-list">
                </ul>
            </div>

            <div class="result-set">
                <div class="set-header">
                    <span id="count2" class="item-count">0 pirates</span>
                </div>
                <ul id="set2" class="result-list">
                </ul>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const listInput = document.getElementById('listInput');
            const splitBtn = document.getElementById('splitBtn');
            const set1Element = document.getElementById('set1');
            const set2Element = document.getElementById('set2');
            const count1Element = document.getElementById('count1');
            const count2Element = document.getElementById('count2');

            splitBtn.addEventListener('click', function() {
                // Get input and split by newline
                const inputText = listInput.value.trim();

                if (!inputText) {
                    alert('Please enter some items first!');
                    return;
                }

                // Split by line breaks and filter out empty lines
                const items = inputText.split('\n')
                    .map(item => item.trim())
                    .filter(item => item.length > 0);

                if (items.length < 2) {
                    alert('Please enter at least two items to split!');
                    return;
                }

                // Shuffle the array randomly using Fisher-Yates algorithm
                const shuffledItems = [...items];
                for (let i = shuffledItems.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [shuffledItems[i], shuffledItems[j]] = [shuffledItems[j], shuffledItems[i]];
                }

                // Split into two sets
                const midpoint = Math.ceil(shuffledItems.length / 2);
                const set1 = shuffledItems.slice(0, midpoint);
                const set2 = shuffledItems.slice(midpoint);

                // Display the results
                displaySet(set1Element, set1, count1Element);
                displaySet(set2Element, set2, count2Element);
            });

            function displaySet(container, items, countElement) {
                // Clear previous content
                container.innerHTML = '';

                // Update count
                countElement.textContent = `${items.length} ${items.length === 1 ? 'item' : 'items'}`;

                if (items.length === 0) {
                    container.innerHTML = '<li class="empty-message">No items in this set</li>';
                    return;
                }

                // Add each item to the list
                items.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    container.appendChild(li);
                });
            }

            // Add example list on load
            listInput.value = "Usopp\nSanji\nKatakuri\nSmoothie";
        });
    </script>
</body>
</html>
