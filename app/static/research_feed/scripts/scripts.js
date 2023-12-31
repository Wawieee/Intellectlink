function resetEnlargedCard() {
    // Reset the state if there is an enlarged card
    const enlargedCard = document.querySelector('.research-card.enlarged');
    if (enlargedCard) {
        enlargedCard.style.display = 'flex';
        enlargedCard.style.transform = 'translateX(0) scale(1)';
        enlargedCard.classList.remove('enlarged');
    }

    // Remove cloned card if it exists
    const clonedCard = document.querySelector('.cloned-card');
    if (clonedCard) {
        clonedCard.remove();
    }

    // Show all cards
    document.querySelectorAll('.research-card').forEach(function (c) {
        c.style.display = 'flex';
    });
}

function slideCard(card) {
    const click = card.getAttribute('data-card-id');
    console.log('Current URL pathname:', window.location.pathname);
    const other_person_id = window.location.pathname.split('/')[2];
    console.log('Extracted other_person_id:', other_person_id);

    const display = document.getElementById('display_' + click);
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    if (card.classList.contains('cloned-card')) {
        return;
    }

    const isEnlarged = card.classList.contains('enlarged');

    if (isEnlarged) {
        // If the card is already enlarged, revert it to the default state
        card.style.display = 'flex';
        card.style.transform = 'translateX(0) scale(1)';
        card.classList.remove('enlarged');

        resetEnlargedCard();
    } else {
        // Reset state and show clicked card
        resetEnlargedCard();

        // Hide all cards except the clicked one
        document.querySelectorAll('.research-card').forEach(function (c) {
            if (c !== card) {
                c.style.display = 'none';
            }
        });

        const clonedCard = document.querySelector('.cloned-card');
        const counterElement = card.querySelector('.click-counter');

        if (!clonedCard) {
            // Increment the click count
            let currentCount = parseInt(counterElement.textContent) || 0
            currentCount++;
            counterElement.textContent = currentCount;

            // Fetch to update click count
            fetch('/update_click_count/' + click, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                
                body: JSON.stringify({ clickCount: currentCount}),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });

            // Create a cloned card
            const newCard = card.cloneNode(true);
            newCard.classList.add('cloned-card');
            card.parentNode.appendChild(newCard);

            // Show the original card
            card.style.display = 'flex';
            card.classList.add('enlarged');
            card.style.transform = 'translateX(-100%) scale(0.8)';

            // Enlarge the new card
            newCard.style.transform = 'scale(2) translateX(21%) translateY(-26%)';
            newCard.style.display = 'flex';
            newCard.querySelector('.card-body').innerHTML = '';
            console.log(other_person_id);
            console.log(click);
           fetch(`/fetch_file/${other_person_id}/view_file/${click}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ click: click }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();  // Change response.blob() to response.text()
            })
            .then(htmlContent => {
                // Set the HTML content in the card body
                newCard.querySelector('.card-body').innerHTML = htmlContent;
                newCard.style.display = 'flex';
                newCard.style.fontSize = '10px';

                // Optionally, you can adjust styles or perform additional actions here

            })
            .catch((error) => {
                console.error('Error:', error);
            });

                        

        }
    }
}

function openRequestModal() {
    $('#requestModal').modal('show');
}

// Log the CSRF token
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
console.log('CSRF Token:', csrfToken);