// --- TAB SWITCHING LOGIC ---
function switchTab(tabId) {
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show the selected tab and highlight the button
    document.getElementById(`${tabId}-content`).classList.add('active');
    document.getElementById(`tab-${tabId}`).classList.add('active');
}

// --- PRESET SCORING DICTIONARIES ---
// Map of the backend variables to their preset values
const presetESPN = {
    // Hitting
    r: 1, b1: 1, b2: 2, b3: 3, hr: 4, rbi: 1, bb_hit: 1, k_hit: -1, sb: 1,
    // Pitching (IP in ESPN is 3 pts per inning, so 1 pt per out)
    ip_outs: 1, er: -2, w: 5, l: -5, sv: 5, k_pitch: 1, h_allow: -1, bb_allow: -1
};

const presetFanGraphs = {
    // FanGraphs Ottoneu Points
    ab: -1, h_hit: 5.6, b2: 2.9, b3: 5.7, hr: 9.4, bb_hit: 3, hbp_hit: 3, sb: 1.9, cs: -2.8,
    ip_outs: 2.46, k_pitch: 2, h_allow: -2.6, bb_allow: -3, hb_pitch: -3, hr_allow: -13.7
};

const presetEthan = {
    // Fill in your specific league settings here
    r: 1, b1: 1, b2: 2, b3: 3, hr: 4, rbi: 1,
    ip_outs: 1, er: -2, k_pitch: 1, w: 5, sv: 5
};

// --- FORM MANAGEMENT ---
function fillInputs(preset) {
    // First, reset everything to 0
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.value = 0;
    });

    // Then, apply the preset values
    for (const [key, value] of Object.entries(preset)) {
        const inputElement = document.getElementById(`w-${key}`);
        if (inputElement) {
            inputElement.value = value;
        }
    }
}

function gatherWeights() {
    const weights = {};
    document.querySelectorAll('input[type="number"]').forEach(input => {
        // Extract the key by removing the 'w-' prefix from the ID
        const key = input.id.replace('w-', '');
        weights[key] = parseFloat(input.value) || 0;
    });
    return weights;
}

// --- EVENT LISTENERS FOR PRESET BUTTONS ---
document.getElementById('btn-espn').addEventListener('click', () => fillInputs(presetESPN));
document.getElementById('btn-fangraphs').addEventListener('click', () => fillInputs(presetFanGraphs));
document.getElementById('btn-ethan').addEventListener('click', () => fillInputs(presetEthan));
document.getElementById('btn-reset').addEventListener('click', () => fillInputs({}));


// --- CORE CALCULATE AND RENDER LOGIC ---
document.getElementById('btn-calculate').addEventListener('click', async () => {
    const calculateBtn = document.getElementById('btn-calculate');
    calculateBtn.innerText = "CALCULATING...";
    calculateBtn.style.backgroundColor = "#ff0000";
    calculateBtn.style.color = "#ffffff";

    const payload = gatherWeights();

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === "success") {
            // Render Actuals
            Plotly.newPlot('actuals-raincloud', data.actuals.raincloud.data, data.actuals.raincloud.layout);
            Plotly.newPlot('actuals-scatter-hit', data.actuals.scatter_hitters.data, data.actuals.scatter_hitters.layout);
            Plotly.newPlot('actuals-scatter-pit', data.actuals.scatter_pitchers.data, data.actuals.scatter_pitchers.layout);
            Plotly.newPlot('actuals-pie-hit', data.actuals.pie_hitters.data, data.actuals.pie_hitters.layout);
            Plotly.newPlot('actuals-pie-sp', data.actuals.pie_sp.data, data.actuals.pie_sp.layout);
            Plotly.newPlot('actuals-pie-rp', data.actuals.pie_rp.data, data.actuals.pie_rp.layout);

            // Render Projections
            Plotly.newPlot('proj-raincloud', data.projections.raincloud.data, data.projections.raincloud.layout);
            Plotly.newPlot('proj-scatter-hit', data.projections.scatter_hitters.data, data.projections.scatter_hitters.layout);
            Plotly.newPlot('proj-scatter-pit', data.projections.scatter_pitchers.data, data.projections.scatter_pitchers.layout);
            Plotly.newPlot('proj-pie-hit', data.projections.pie_hitters.data, data.projections.pie_hitters.layout);
            Plotly.newPlot('proj-pie-sp', data.projections.pie_sp.data, data.projections.pie_sp.layout);
            Plotly.newPlot('proj-pie-rp', data.projections.pie_rp.data, data.projections.pie_rp.layout);
        } else {
            alert("Error processing data.");
        }
    } catch (error) {
        console.error("Fetch error:", error);
        alert("Failed to connect to the backend.");
    } finally {
        calculateBtn.innerText = "RUN CALCULATIONS";
        calculateBtn.style.backgroundColor = "#ffff00";
        calculateBtn.style.color = "#000000";
    }
});

// --- PDF GENERATION LOGIC ---
document.getElementById('btn-pdf').addEventListener('click', () => {
    const element = document.body;
    const opt = {
        margin:       0.5,
        filename:     'fantasy_scoring_sandbox.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };
    
    // Check if html2pdf is loaded
    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(element).save();
    } else {
        alert("Please add the html2pdf script tag to your index.html file.");
    }
});