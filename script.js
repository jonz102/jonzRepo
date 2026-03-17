const categories = ['A', 'B', 'C', 'D', 'E', 'F'];
let counts = {};
categories.forEach(cat => counts[cat] = 0);

const appDiv = document.getElementById('app');

function renderCounters() {
    appDiv.innerHTML = ''; // Clear previous counters
    categories.forEach(cat => {
        const counterDiv = document.createElement('div');
        counterDiv.className = 'counter-item';
        counterDiv.innerHTML = `
            <h2>Category ${cat}</h2>
            <div class="count-display" id="count-${cat}">${counts[cat]}</div>
            <div class="counter-buttons">
                <button class="counter-btn decrement" onclick="changeCount('${cat}', -1)">−</button>
                <button class="counter-btn increment" onclick="changeCount('${cat}', 1)">+</button>
            </div>
        `;
        appDiv.appendChild(counterDiv);
    });
}

function changeCount(category, change) {
    counts[category] += change;
    
    // Prevent negative counts
    if (counts[category] < 0) {
        counts[category] = 0;
    }
    
    const countElement = document.getElementById(`count-${category}`);
    countElement.innerText = counts[category];
    
    // Add animation effect
    countElement.style.transform = 'scale(1.2)';
    countElement.style.color = change > 0 ? '#28a745' : '#dc3545';
    
    setTimeout(() => {
        countElement.style.transform = 'scale(1)';
        countElement.style.color = '#667eea';
    }, 200);
}

function resetAllCounters() {
    categories.forEach(cat => {
        counts[cat] = 0;
        const countElement = document.getElementById(`count-${cat}`);
        if (countElement) {
            countElement.innerText = 0;
            // Add reset animation
            countElement.style.transform = 'scale(0.8)';
            countElement.style.color = '#6c757d';
            
            setTimeout(() => {
                countElement.style.transform = 'scale(1)';
                countElement.style.color = '#667eea';
            }, 150);
        }
    });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    renderCounters();
    
    // Add event listener for reset button
    const resetButton = document.getElementById('resetAll');
    if (resetButton) {
        resetButton.addEventListener('click', resetAllCounters);
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key === 'r') {
        event.preventDefault();
        resetAllCounters();
    }
});
