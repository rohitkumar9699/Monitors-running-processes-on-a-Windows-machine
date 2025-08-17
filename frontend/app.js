let allProcesses = [];
let processView = 'table';

function showTab(tab) {
    document.getElementById('systemTab').style.display = tab === 'system' ? 'block' : 'none';
    document.getElementById('processesTab').style.display = tab === 'processes' ? 'block' : 'none';
    document.getElementById('tabSystem').classList.toggle('active', tab === 'system');
    document.getElementById('tabProcesses').classList.toggle('active', tab === 'processes');
}

function setProcessView(view) {
    processView = view;
    renderProcesses();
}

async function loadHosts() {
    const base = document.getElementById('baseUrl').value.trim();
    try {
        const resp = await fetch(`${base}/api/hosts/`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();

        const hostSelect = document.getElementById('hostname');
        hostSelect.innerHTML = '';
        data.hosts.forEach(h => {
            const opt = document.createElement('option');
            opt.value = h.hostname;
            opt.textContent = h.hostname;
            hostSelect.appendChild(opt);
        });

        if (data.hosts.length > 0) {
            hostSelect.value = data.hosts[0].hostname;
            loadLatest();
        }
    } catch (err) {
        alert("Error loading hosts: " + err.message);
    }
}

async function loadLatest() {
    const base = document.getElementById('baseUrl').value.trim();
    const hn = document.getElementById('hostname').value;
    if (!hn) { alert("Select hostname"); return; }

    try {
        const resp = await fetch(`${base}/api/latest?hostname=${encodeURIComponent(hn)}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();

        const sys = data.system_info || {};
        const sysHTML = `
            <tr><th>Name</th><td>${sys.name || ''}</td></tr>
            <tr><th>Operating System</th><td>${sys.os || ''}</td></tr>
            <tr><th>Processor</th><td>${sys.processor || ''}</td></tr>
            <tr><th>Number of Cores</th><td>${sys.cores || ''}</td></tr>
            <tr><th>Number of Threads</th><td>${sys.threads || ''}</td></tr>
            <tr><th>RAM (GB)</th><td>${sys.ram_gb || ''}</td></tr>
            <tr><th>Used RAM (GB)</th><td>${sys.used_ram_gb || ''}</td></tr>
            <tr><th>Available RAM (GB)</th><td>${sys.available_ram_gb || ''}</td></tr>
            <tr><th>Storage Free (GB)</th><td>${sys.storage_free_gb || ''}</td></tr>
            <tr><th>Storage Total (GB)</th><td>${sys.storage_total_gb || ''}</td></tr>
            <tr><th>Storage Used (GB)</th><td>${sys.storage_used_gb || ''}</td></tr>
        `;
        document.getElementById('systemTable').innerHTML = sysHTML;

        allProcesses = data.snapshot.processes || [];
        const date = new Date(data.snapshot.created_at);
        document.getElementById("update").textContent = ` Updated at ${date.toLocaleString()}`;
        renderProcesses();
    } catch (err) {
        alert("Error loading data of user: " + err.message);
    }
}

function renderProcesses() {
    const container = document.getElementById('processTableContainer');
    container.innerHTML = '';

    if (processView === 'table') {
        let html = `<table><tr>
            <th>Sr. No</th>
            <th>Name</th>
            <th>Memory Usage (MB)</th>
            <th>CPU Usage (%)</th>
            <th>PPID</th>
        </tr>`;
        let i = 1;
        allProcesses.forEach(p => {
            html += `<tr>
                <td>${i}</td>
                <td>${p.name}</td>
                <td>${p.memory_mb ?? ''}</td>
                <td>${p.cpu_percent ?? ''}</td>
                <td>${p.ppid ?? ''}</td>
            </tr>`;
            i++;
        });
        html += '</table>';
        container.innerHTML = html;
    } else {
        const byPid = new Map();
        const roots = [];
        allProcesses.forEach(p => { p.children = []; byPid.set(p.pid, p); });
        allProcesses.forEach(p => {
            if (p.ppid && byPid.has(p.ppid)) byPid.get(p.ppid).children.push(p);
            else roots.push(p);
        });
        const treeEl = document.createElement('div');
        roots.forEach(r => treeEl.appendChild(renderTreeNode(r)));
        container.appendChild(treeEl);
    }
}

function renderTreeNode(proc) {
    const wrapper = document.createElement('div');
    wrapper.className = 'tree-node';

    const label = document.createElement('div');
    label.className = 'tree-label';
    const toggle = document.createElement('span');
    toggle.className = 'tree-toggle';
    toggle.textContent = proc.children && proc.children.length > 0 ? '▼' : '';
    label.prepend(toggle);
    label.innerHTML += `<b>${proc.name}</b> (PID: ${proc.pid}) 
        <span>CPU: ${proc.cpu_percent ?? ''}%</span>
        <span>Mem: ${proc.memory_mb ?? ''} MB</span>`;
    wrapper.appendChild(label);

    if (proc.children && proc.children.length > 0) {
        let expanded = true;
        const childrenContainer = document.createElement('div');
        proc.children.forEach(c => childrenContainer.appendChild(renderTreeNode(c)));
        wrapper.appendChild(childrenContainer);

        label.addEventListener('click', () => {
            expanded = !expanded;
            childrenContainer.style.display = expanded ? 'block' : 'none';
            toggle.textContent = expanded ? '▼' : '▶';
        });
    }
    return wrapper;
}

document.addEventListener('DOMContentLoaded', loadHosts);
