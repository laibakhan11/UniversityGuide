    const grid = document.getElementById('universities-grid');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    async function loadUniversities() {
      try {
        const response = await fetch('http://localhost:8000/api/universities');
        if (!response.ok) throw new Error('Failed to load universities');

        const universities = await response.json();

        loading.style.display = 'none';
        grid.innerHTML = ''; // Clear grid

        universities.forEach(uni => {
          const card = document.createElement('div');
          card.className = 'uni-card';
          card.innerHTML = `
            <h3>${uni.shortName || uni.name}</h3>
            <p>${uni.fullName || uni.name}</p>
            <a href="university.html?name=${uni.shortName}" class="view-btn">View</a>
          `;
          grid.appendChild(card);
        });

      } catch (err) {
        loading.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'Error: Could not load universities. Is backend running?';
        console.error(err);
      }
    }

    // Load universities when page opens
    loadUniversities();