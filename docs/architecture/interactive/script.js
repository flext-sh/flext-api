// FLEXT-API Architecture Documentation JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Initialize interactive features
  initializeNavigation();
  loadADRs();
  loadQualityMetrics();
  setupImageModal();
});

// Navigation highlighting
function initializeNavigation() {
  const navLinks = document.querySelectorAll(".nav-link");
  const sections = document.querySelectorAll("section[id]");

  function highlightNavigation() {
    const scrollPosition = window.scrollY + 100;

    sections.forEach((section) => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute("id");

      if (
        scrollPosition >= sectionTop &&
        scrollPosition < sectionTop + sectionHeight
      ) {
        navLinks.forEach((link) => {
          link.classList.remove("active");
          if (link.getAttribute("href") === `#${sectionId}`) {
            link.classList.add("active");
          }
        });
      }
    });
  }

  window.addEventListener("scroll", highlightNavigation);
  highlightNavigation(); // Initial call
}

// Load ADR list dynamically
async function loadADRs() {
  const adrList = document.getElementById("adr-list");

  try {
    // In a real implementation, this would fetch ADR data
    // For now, we'll simulate with static data
    const adrs = [
      { number: "001", title: "FLEXT-Core Dependency", status: "Accepted" },
      {
        number: "002",
        title: "Railway-Oriented Error Handling",
        status: "Accepted",
      },
      {
        number: "003",
        title: "Protocol Plugin Architecture",
        status: "Accepted",
      },
    ];

    let html = '<div class="adr-grid">';
    adrs.forEach((adr) => {
      html += `
                <div class="adr-card">
                    <h4>ADR-${adr.number}</h4>
                    <p>${adr.title}</p>
                    <span class="status status-${adr.status.toLowerCase()}">${adr.status}</span>
                    <a href="../decisions/${adr.number}-${adr.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.md" class="btn">View ADR</a>
                </div>
            `;
    });
    html += "</div>";

    adrList.innerHTML = html;

    // Add ADR card styles
    const style = document.createElement("style");
    style.textContent = `
            .adr-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
            }
            .adr-card {
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            }
            .adr-card h4 {
                color: #667eea;
                margin-bottom: 0.5rem;
            }
            .status {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: bold;
                margin: 0.5rem 0;
            }
            .status-accepted {
                background: #d4edda;
                color: #155724;
            }
        `;
    document.head.appendChild(style);
  } catch (error) {
    adrList.innerHTML = "<p>Error loading ADRs</p>";
    console.error("Error loading ADRs:", error);
  }
}

// Load quality metrics dynamically
async function loadQualityMetrics() {
  const metricsDiv = document.getElementById("quality-metrics");

  try {
    // Simulate loading quality metrics
    const metrics = {
      overall_score: 61.6,
      audit_compliance: 46.5,
      link_health: 62.7,
      style_consistency: 76.9,
      content_quality: 95.4,
      maintenance_coverage: 0.0,
    };

    let html = '<div class="metrics-grid">';
    Object.entries(metrics).forEach(([key, value]) => {
      const displayName = key
        .replace(/_/g, " ")
        .replace(/\w/g, (l) => l.toUpperCase());
      const color = value >= 80 ? "high" : value >= 60 ? "medium" : "low";

      html += `
                <div class="metric-item ${color}">
                    <h4>${displayName}</h4>
                    <div class="metric-value">${value}%</div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: ${value}%"></div>
                    </div>
                </div>
            `;
    });
    html += "</div>";

    metricsDiv.innerHTML = html;

    // Add metric styles
    const style = document.createElement("style");
    style.textContent = `
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
            }
            .metric-item {
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            }
            .metric-item.high { border-left: 4px solid #28a745; }
            .metric-item.medium { border-left: 4px solid #ffc107; }
            .metric-item.low { border-left: 4px solid #dc3545; }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                margin: 0.5rem 0;
            }
            .metric-bar {
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 0.5rem;
            }
            .metric-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                transition: width 0.3s ease;
            }
        `;
    document.head.appendChild(style);
  } catch (error) {
    metricsDiv.innerHTML = "<p>Error loading quality metrics</p>";
    console.error("Error loading quality metrics:", error);
  }
}

// Setup image modal for diagram viewing
function setupImageModal() {
  // Create modal elements
  const modal = document.createElement("div");
  modal.id = "image-modal";
  modal.innerHTML = `
        <div class="modal-content">
            <span class="modal-close">&times;</span>
            <img id="modal-image" src="" alt="Architecture Diagram">
        </div>
    `;

  const style = document.createElement("style");
  style.textContent = `
        #image-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }
        .modal-content {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 1200px;
            position: relative;
            top: 50%;
            transform: translateY(-50%);
        }
        .modal-close {
            position: absolute;
            top: -40px;
            right: 0;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        #modal-image {
            width: 100%;
            height: auto;
        }
    `;

  document.body.appendChild(style);
  document.body.appendChild(modal);

  // Add click handlers for image links
  document.querySelectorAll(".image-link").forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const img = document.getElementById("modal-image");
      img.src = this.href;
      modal.style.display = "block";
    });
  });

  // Close modal when clicking X or outside
  document.querySelector(".modal-close").addEventListener("click", () => {
    modal.style.display = "none";
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
}

// Utility functions
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
