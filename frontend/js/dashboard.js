/**
 * dashboard.js — Stats cards and Chart.js charts.
 */

const Dashboard = (() => {
  let statusChart   = null;
  let priorityChart = null;
  let rateChart     = null;

  function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      grid:  isDark ? 'rgba(255,255,255,.07)' : 'rgba(0,0,0,.07)',
      label: isDark ? '#8b90ad' : '#6b7094',
    };
  }

  async function load() {
    try {
      const s = await Api.getTaskStats();
      renderStats(s);
      renderCharts(s);
    } catch (err) {
      Toast.show('Failed to load dashboard stats', 'error');
    }
  }

  function renderStats(s) {
    document.getElementById('stat-total').textContent     = s.total;
    document.getElementById('stat-todo').textContent      = s.todo;
    document.getElementById('stat-inprogress').textContent= s.in_progress;
    document.getElementById('stat-completed').textContent = s.completed;
    document.getElementById('stat-duetoday').textContent  = s.due_today;
    document.getElementById('stat-overdue').textContent   = s.overdue;
  }

  function renderCharts(s) {
    const { grid, label } = getChartColors();
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary').trim();

    // ── Status doughnut ─────────────────────────────────────
    const statusCtx = document.getElementById('status-chart').getContext('2d');
    if (statusChart) statusChart.destroy();
    statusChart = new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: ['To Do', 'In Progress', 'Completed', 'Cancelled'],
        datasets: [{
          data: [s.todo, s.in_progress, s.completed, s.cancelled],
          backgroundColor: ['#6366f1','#a855f7','#22c55e','#6b7280'],
          borderWidth: 0,
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '70%',
        plugins: {
          legend: { position: 'bottom', labels: { color: label, padding: 12, font: { size: 11 } } },
          tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.raw}` } },
        },
      },
    });

    // ── Priority bar ─────────────────────────────────────────
    const priorityCtx = document.getElementById('priority-chart').getContext('2d');
    if (priorityChart) priorityChart.destroy();
    priorityChart = new Chart(priorityCtx, {
      type: 'bar',
      data: {
        labels: ['Urgent', 'High', 'Medium', 'Low'],
        datasets: [{
          data: [
            s.priority_breakdown.urgent,
            s.priority_breakdown.high,
            s.priority_breakdown.medium,
            s.priority_breakdown.low,
          ],
          backgroundColor: ['#ef4444','#f97316','#f59e0b','#22c55e'],
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: grid }, ticks: { color: label } },
          y: { grid: { color: grid }, ticks: { color: label, stepSize: 1 }, beginAtZero: true },
        },
      },
    });

    // ── Completion rate gauge ─────────────────────────────────
    const rate = s.completion_rate;
    document.getElementById('rate-label').textContent = `${rate}%`;
    document.getElementById('rate-meta').innerHTML = `
      <div>Total tasks: <strong>${s.total}</strong></div>
      <div>Completed: <strong>${s.completed}</strong></div>
      <div>Overdue: <strong style="color:var(--danger)">${s.overdue}</strong></div>
      <div>Due today: <strong style="color:var(--warning)">${s.due_today}</strong></div>
    `;
    const rateCtx = document.getElementById('rate-chart').getContext('2d');
    if (rateChart) rateChart.destroy();
    rateChart = new Chart(rateCtx, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [rate, 100 - rate],
          backgroundColor: ['#6366f1', 'rgba(99,102,241,.1)'],
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '80%',
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        rotation: -90, circumference: 180,
      },
    });
  }

  // Greeting based on time of day
  function setGreeting() {
    const h = new Date().getHours();
    const g = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
    const email = sessionStorage.getItem('tm_user_email') || '';
    document.getElementById('greeting-text').textContent = `${g}! ${email ? '(' + email + ')' : ''}`;
  }

  return { load, setGreeting };
})();
