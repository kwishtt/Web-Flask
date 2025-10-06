document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".primary-nav");

    if (navToggle && nav) {
        navToggle.addEventListener("click", () => {
            nav.classList.toggle("active");
        });
    }

    document.querySelectorAll(".flash-close").forEach((button) => {
        button.addEventListener("click", (event) => {
            event.currentTarget.parentElement.remove();
        });
    });

    setTimeout(() => {
        document.querySelectorAll(".flash").forEach((flash) => {
            flash.classList.add("fade-out");
            flash.addEventListener("transitionend", () => flash.remove(), {
                once: true,
            });
        });
    }, 4000);

    document.querySelectorAll("img[data-fallback]").forEach((img) => {
        img.addEventListener("error", () => {
            const fallback = img.getAttribute("data-fallback");
            if (fallback && img.src !== fallback) {
                img.src = fallback;
            }
        });
    });

    // Random data generation for movie prediction form
    const randomBtn = document.getElementById('randomBtn');
    if (randomBtn) {
        randomBtn.addEventListener('click', generateRandomData);
    }

    function generateRandomData() {
        // Movie titles - Blockbuster style
        const movieTitles = [
            "Điệp Viên 007: Skyfall", "Avengers: Endgame", "Titanic", "The Dark Knight",
            "Inception", "Pulp Fiction", "The Shawshank Redemption", "Forrest Gump",
            "The Matrix", "Goodfellas", "The Silence of the Lambs", "Schindler's List",
            "Fight Club", "The Lord of the Rings", "Star Wars", "Jurassic Park",
            "Terminator 2", "The Godfather", "Casablanca", "Citizen Kane",
            "Gone with the Wind", "Lawrence of Arabia", "Ben-Hur", "Gandhi",
            "Amadeus", "Rain Man", "Driving Miss Daisy", "Platoon", "The Last Emperor",
            "Moonlight", "Spotlight", "Green Book", "CODA", "Everything Everywhere All at Once"
        ];

        // Genres - Popular genres with higher success rate
        const genres = ["Action", "Adventure", "Science Fiction", "Drama", "Comedy", "Thriller"];

        // Countries - Major markets
        const countries = ["United States of America", "United Kingdom", "France"];

        // Generate random values BIASED TOWARD SUCCESS
        const randomTitle = movieTitles[Math.floor(Math.random() * movieTitles.length)];
        
        // Budget: $30M - $180M (blockbuster range)
        const randomBudget = Math.floor(Math.random() * 150000000) + 30000000;
        
        const randomGenre = genres[Math.floor(Math.random() * genres.length)];
        
        // Vote Average: 6.0 - 8.5 (good to excellent range, ensures >= 6.5 often)
        const randomVoteAverage = (Math.random() * 2.5 + 6.0).toFixed(1);
        
        // Vote Count: 5,000 - 45,000 (popular movies)
        const randomVoteCount = Math.floor(Math.random() * 40000) + 5000;
        
        // Runtime: 100 - 160 minutes (standard blockbuster length)
        const randomRuntime = Math.floor(Math.random() * 60) + 100;
        
        // Release Year: 2015 - 2024 (recent movies)
        const randomYear = Math.floor(Math.random() * 10) + 2015;
        
        // Release Month: Summer (5,6,7) or Holiday (11,12) seasons
        const popularMonths = [5, 6, 7, 11, 12];
        const randomMonth = popularMonths[Math.floor(Math.random() * popularMonths.length)];
        
        const randomCountry = countries[Math.floor(Math.random() * countries.length)];

        // Fill form fields
        document.getElementById('title').value = randomTitle;
        document.getElementById('budget').value = randomBudget;
        document.getElementById('genre').value = randomGenre;
        document.getElementById('director_rating').value = randomVoteAverage;
        document.getElementById('actor_rating').value = randomVoteCount;
        document.getElementById('runtime').value = randomRuntime;
        document.getElementById('release_year').value = randomYear;
        document.getElementById('release_month').value = randomMonth;
        document.getElementById('country').value = randomCountry;

                // Enhanced visual feedback with magical effects
        const originalText = randomBtn.innerHTML;
        const originalBg = randomBtn.style.background;

        // Add success class for magical animation
        randomBtn.classList.add('success');
        randomBtn.innerHTML = '✨ Đã tạo dữ liệu!';
        randomBtn.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
        randomBtn.style.boxShadow = '0 8px 25px rgba(39, 174, 96, 0.4)';

        // Animate form fields with staggered magical effects
        const formFields = ['title', 'budget', 'genre', 'director_rating', 'actor_rating', 'runtime', 'release_year', 'release_month', 'country'];
        formFields.forEach((fieldId, index) => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Reset animation
                field.style.animation = 'none';
                setTimeout(() => {
                    field.style.animation = 'magicalBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                    field.style.animationDelay = `${index * 0.1}s`;
                    field.style.animationFillMode = 'both';

                    // Add glow effect
                    field.style.boxShadow = '0 0 20px rgba(139, 92, 246, 0.3)';
                    setTimeout(() => {
                        field.style.boxShadow = '';
                    }, 1000);
                }, 10);
            }
        });

        // Create particle burst effect
        const createParticles = () => {
            for (let i = 0; i < 8; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle-burst';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 0.5 + 's';
                randomBtn.appendChild(particle);

                setTimeout(() => {
                    if (particle.parentNode) {
                        particle.parentNode.removeChild(particle);
                    }
                }, 1000);
            }
        };

        createParticles();

        // Reset button after animation
        setTimeout(() => {
            randomBtn.innerHTML = originalText;
            randomBtn.classList.remove('success');
            randomBtn.style.background = originalBg;
            randomBtn.style.boxShadow = '';
        }, 2500);
    }
});
