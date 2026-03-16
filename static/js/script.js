// =============================================
// Scroll fade-up animation
// =============================================
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-up').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
  observer.observe(el);
});


// =============================================
// Fetch projects from REST API
// and display them dynamically
// =============================================
async function loadProjectsFromAPI() {
  const container = document.getElementById('api-projects-container');
  if (!container) return;   // only runs on pages that have this div

  try {
    // Call our Flask API
    const response = await fetch('/api/projects');
    const projects = await response.json();

    if (projects.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:40px; color:#64748b;">
          No projects yet. Add them from the Admin Panel.
        </div>`;
      return;
    }

    // Build HTML cards from API data
    container.innerHTML = projects.map(project => `
      <div class="project-card fade-up">
        <div class="project-type">Project</div>
        <div class="project-title">${project.title}</div>
        <div class="project-desc">${project.description}</div>
        <div class="tech-tags">
          ${project.tech_stack.split(',').map(tech =>
            `<span class="tech-tag">${tech.trim()}</span>`
          ).join('')}
        </div>
        <div style="margin-top:16px; display:flex; gap:10px;">
          ${project.github_url ?
            `<a href="${project.github_url}" target="_blank"
                class="outline-btn" style="padding:8px 18px; font-size:12px;">
               GitHub
             </a>` : ''}
        </div>
      </div>
    `).join('');

    // Re-apply fade-up animation to new cards
    document.querySelectorAll('#api-projects-container .fade-up').forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(24px)';
      el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
      observer.observe(el);
    });

  } catch (error) {
    console.error('API Error:', error);
    container.innerHTML = `
      <div style="color:#f87171; padding:20px;">
        Could not load projects. Is the server running?
      </div>`;
  }
}

// Run when page loads
loadProjectsFromAPI();


// =============================================
// Navbar active link highlighter
// =============================================
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-links a').forEach(link => {
  if (link.getAttribute('href') === currentPath) {
    link.style.color = '#a78bfa';
    link.style.fontWeight = '500';
  }
});


// =============================================
// Contact form success animation
// =============================================
const flashMsg = document.querySelector('.flash-success');
if (flashMsg) {
  setTimeout(() => {
    flashMsg.style.transition = 'opacity 0.5s ease';
    flashMsg.style.opacity = '0';
    setTimeout(() => flashMsg.remove(), 500);
  }, 3000);
}