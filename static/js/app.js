// --- TAB SWITCHING LOGIC ---
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${tabId}-content`).classList.add('active');
    document.getElementById(`tab-${tabId}`).classList.add('active');

    setTimeout(() => {
        document.querySelectorAll(`#${tabId}-content .graph-container`).forEach(el => {
            Plotly.relayout(el, { autosize: true });
        });
    }, 10);
}

// --- PRESET SCORING DICTIONARIES ---
// Map of the backend variables to their preset values
const presetESPN = {
    // League Rosters
    teams: 10,
    hitters: 10,
    sp: 7,
    rp: 2,
    // Hitting
    r: 1,
    tb: 1,
    rbi: 1,
    bb_hit: 1,
    k_hit: -1,
    sb: 1,
    // Pitching
    ip_outs: 1,
    h_allow: -1,
    er: -2,
    hd: 2,
    bb_allow: -1,
    k_pitch: 1,
    w: 5,
    l: -2,
    sv: 5
};

const presetFanGraphs = {
    // League Rosters
    teams: 14,
    hitters: 10,
    sp: 6,
    rp: 2,
    // Hitting
    ab: -1.0,
    h_hit: 5.6,
    b2: 2.9,
    b3: 5.7,
    hr: 9.4,
    bb_hit: 3.0,
    hbp_hit: 3.0,
    sb: 1.9,
    cs: -2.8,
    // Pitching
    ip_outs: 2.47,
    k_pitch: 2.0,
    h_allow: -2.6,
    bb_allow: -3.0,
    hb_pitch: -3.0,
    hr_allow: -12.3,
    sv: 5.0,
    hd: 4.0
};

const presetEthan = {
    // League Rosters
    teams: 12,
    hitters: 11,
    sp: 6,
    rp: 1,
    // Hitting
    r: 1,
    b1: 0.5,
    xbh: 0.5,
    tb: 1,
    rbi: 1,
    bb_hit: 1,
    k_hit: -0.5,
    hbp_hit: 0.5,
    sb: 1,
    cyc: 25,
    gshr: 5,
    // Pitching
    ip_outs: 1.1,
    h_allow: -1,
    er: -2,
    bb_allow: -1,
    k_pitch: 1.1,
    balks: -1,
    qs: 4,
    cg: 10,
    sho: 5,
    nh: 15,
    pg: 30,
    w: 2,
    l: -2,
    sv: 5,
    bs: -3,
    hd: 3
};

// --- FORM MANAGEMENT ---
function fillInputs(preset) {
    // First, reset everything to 0
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.value = 0;
    });

    // Then, apply the preset values
    for (const [key, value] of Object.entries(preset)) {
        // Dynamically check for either the weights prefix (w-) or rosters prefix (r-)
        const inputElement = document.getElementById(`w-${key}`) || document.getElementById(`r-${key}`);
        if (inputElement) {
            inputElement.value = value;
        }
    }
}

function gatherPayload() {
    const payload = {
        weights: {},
        rosters: {}
    };

    document.querySelectorAll('input[type="number"]').forEach(input => {
        if (input.id.startsWith('w-')) {
            const key = input.id.replace('w-', '');
            payload.weights[key] = parseFloat(input.value) || 0;
        } else if (input.id.startsWith('r-')) {
            const key = input.id.replace('r-', '');
            payload.rosters[key] = parseInt(input.value) || 0;
        }
    });

    return payload;
}

// --- EVENT LISTENERS FOR PRESET BUTTONS ---
document.getElementById('btn-espn').addEventListener('click', () => fillInputs(presetESPN));
document.getElementById('btn-fangraphs').addEventListener('click', () => fillInputs(presetFanGraphs));
document.getElementById('btn-ethan').addEventListener('click', () => fillInputs(presetEthan));
document.getElementById('btn-reset').addEventListener('click', () => fillInputs({}));


// --- CORE CALCULATE AND RENDER LOGIC ---
document.getElementById('btn-calculate').addEventListener('click', async () => {
    const payload = gatherPayload();

    // Frontend Validation Check
    if (
        payload.rosters.teams === 0 || 
        (payload.rosters.hitters === 0 && payload.rosters.sp === 0 && payload.rosters.rp === 0)
    ) {
        alert("Please specify the Number of Teams and at least one roster spot (Hitters, SPs, or RPs) before calculating.");
        return; 
    }

    const calculateBtn = document.getElementById('btn-calculate');
    calculateBtn.innerText = "CALCULATING...";
    calculateBtn.style.backgroundColor = "#3b82f6";

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
            Plotly.newPlot('actual-power-balance', data.actuals.stacked.data, data.actuals.stacked.layout);

            // Render Projections
            Plotly.newPlot('proj-raincloud', data.projections.raincloud.data, data.projections.raincloud.layout);
            Plotly.newPlot('proj-scatter-hit', data.projections.scatter_hitters.data, data.projections.scatter_hitters.layout);
            Plotly.newPlot('proj-scatter-pit', data.projections.scatter_pitchers.data, data.projections.scatter_pitchers.layout);
            Plotly.newPlot('proj-pie-hit', data.projections.pie_hitters.data, data.projections.pie_hitters.layout);
            Plotly.newPlot('proj-pie-sp', data.projections.pie_sp.data, data.projections.pie_sp.layout);
            Plotly.newPlot('proj-pie-rp', data.projections.pie_rp.data, data.projections.pie_rp.layout);
            Plotly.newPlot('proj-power-balance', data.projections.stacked.data, data.projections.stacked.layout);
        } else {
            alert("Error processing data.");
        }
    } catch (error) {
        console.error("Fetch error:", error);
        alert("Failed to connect to the backend.");
    } finally {
        calculateBtn.innerText = "RUN CALCULATIONS";
        calculateBtn.style.backgroundColor = "#f59e0b";
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