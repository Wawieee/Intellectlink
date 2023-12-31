function slideCard(card) {
    console.log("Entering slideCard function");
    const click = card.getAttribute('data-card-id');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const isPrivate = card.classList.contains('private');

    if (card.classList.contains('cloned-card') || isPrivate) {
        // If it's a cloned card or private card, do nothing
        return;
    }

    const isEnlarged = card.classList.contains('enlarged');

    if (isEnlarged) {
        console.log("Card is already enlarged");
        // If the card is already enlarged, revert it to the default state
        card.style.display = 'flex';
        card.style.transform = 'translateX(0) scale(1)';
        card.classList.remove('enlarged');

        resetEnlargedCard();
    } else {
        console.log("Enlarging the card");
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
            let currentCount = parseInt(counterElement.textContent) || 0;
            currentCount++;
            counterElement.textContent = currentCount;

            // Fetch to update click count
            fetch('/update_click_count/' + click, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ clickCount: currentCount }),
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

            // Check if it's a private card
            if (isPrivate) {
                // Redirect to the specified route for other_profile
                const otherPersonId = data.other_person_id;
                const otherViewFileUrl = `/other_profile/${otherPersonId}/other_viewfile/${click}`;
                window.location.href = otherViewFileUrl;
            } else {
                // Fetch PDF Blob from the server
                fetch('/fetch_pdf/' + click, {
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
                        return response.blob();
                    })
                    .then(blob => {
                        // Create a Blob URL for the PDF
                        const pdfBlobUrl = URL.createObjectURL(blob);

                        // Create an embed element for the PDF
                        const pdfEmbed = document.createElement('embed');
                        pdfEmbed.setAttribute('src', `${pdfBlobUrl}#view=FitH&scrollbar=1&toolbar=1&statusbar=1&messages=1&navpanes=1`);
                        pdfEmbed.setAttribute('type', 'application/pdf');
                        pdfEmbed.style.width = '100%';
                        pdfEmbed.style.height = '100%';

                        // Append the PDF embed element to the card body
                        newCard.querySelector('.card-body').appendChild(pdfEmbed);

                        // Hide overflow on the new card if needed
                        newCard.querySelector('.card-body').style.overflow = 'auto';

                        // Adjust the font size of the new card
                        newCard.querySelectorAll('.card-title, .card-text').forEach(function (element) {
                            element.style.fontSize = '1em';
                        });

                        newCard.querySelectorAll('.card-text').forEach(function (element) {
                            element.style.fontSize = '.5em';
                        });
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
            }
        }
    }
}
