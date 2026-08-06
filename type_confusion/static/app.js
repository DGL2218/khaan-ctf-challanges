let targetBalance = 500.0;

async function fetchWallet() {
    try {
        const res = await fetch('/api/wallet');
        const data = await res.json();
        if (data.status === 'success') {
            updateUI(data.wallet, data.target_balance);
        }
    } catch (err) {
        console.error("Failed to fetch wallet:", err);
    }
}

function updateUI(wallet, target) {
    if (target) targetBalance = target;
    
    document.getElementById('bal-USD').textContent = `$${wallet.USD.toFixed(2)}`;
    document.getElementById('bal-EUR').textContent = `€${wallet.EUR.toFixed(2)}`;
    document.getElementById('bal-JPY').textContent = `¥${wallet.JPY.toFixed(0)}`;
    document.getElementById('bal-MINI').textContent = `${wallet.MINI.toFixed(4)} MINI`;

    // Progress bar
    const progress = Math.min(100, (wallet.USD / targetBalance) * 100);
    document.getElementById('target-progress').style.width = `${progress}%`;
    document.getElementById('progress-text').textContent = `$${wallet.USD.toFixed(2)} / $${targetBalance.toFixed(2)} USD`;
}

async function handleExchange(e) {
    e.preventDefault();
    const from_currency = document.getElementById('from-curr').value;
    const to_currency = document.getElementById('to-curr').value;
    const amount = parseFloat(document.getElementById('swap-amount').value);

    try {
        const res = await fetch('/api/exchange', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ from_currency, to_currency, amount })
        });
        const data = await res.json();
        if (data.status === 'success') {
            updateUI(data.wallet);
            document.getElementById('swap-amount').value = '';
        } else {
            alert(data.message);
        }
    } catch (err) {
        console.error("Exchange error:", err);
    }
}

async function resetWallet() {
    try {
        const res = await fetch('/api/reset', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            updateUI(data.wallet);
            document.getElementById('flag-box').classList.add('hidden');
        }
    } catch (err) {
        console.error("Reset error:", err);
    }
}

async function claimFlag() {
    try {
        const res = await fetch('/api/flag');
        const data = await res.json();
        const flagBox = document.getElementById('flag-box');
        const flagCode = document.getElementById('flag-code');

        if (data.status === 'success') {
            flagBox.classList.remove('hidden');
            flagCode.textContent = data.flag;
        } else {
            alert(data.message);
        }
    } catch (err) {
        console.error("Flag error:", err);
    }
}

function updateRateDisplay() {
    const from = document.getElementById('from-curr').value;
    const to = document.getElementById('to-curr').value;
    const rates = { USD: 1.0, EUR: 0.92, JPY: 155.5, MINI: 100.0 };
    
    let rate = rates[to] / rates[from];
    document.getElementById('rate-preview').textContent = `Rate: 1 ${from} = ${rate.toFixed(4)} ${to}`;
}

document.addEventListener('DOMContentLoaded', fetchWallet);
