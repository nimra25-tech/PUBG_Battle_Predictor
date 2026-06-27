// =====================================================
// PUBG BATTLE PREDICTOR
// ANIMATION ENGINE
// =====================================================


// ==========================================
// RANDOM PLAYER MOVEMENT
// ==========================================

function movePlayer() {

    let player =
    document.getElementById("player-marker");

    if (!player) return;

    let x =
    Math.floor(
        Math.random() * 400
    );

    let y =
    Math.floor(
        Math.random() * 250
    );

    player.style.left =
    x + "px";

    player.style.top =
    y + "px";
}


// Every 2 Seconds

setInterval(
    movePlayer,
    2000
);


// ==========================================
// ZONE PULSE EFFECT
// ==========================================

function pulseZone() {

    let zone =
    document.querySelector(".zone");

    if (!zone) return;

    zone.style.boxShadow =
    "0px 0px 40px cyan";

    setTimeout(() => {

        zone.style.boxShadow =
        "0px 0px 10px cyan";

    }, 700);
}


setInterval(
    pulseZone,
    1200
);


// ==========================================
// DUST PARTICLES
// ==========================================

function createDust() {

    const dust =
    document.createElement("div");

    dust.classList.add(
        "dust-particle"
    );

    dust.style.left =
    Math.random() * window.innerWidth +
    "px";

    dust.style.top =
    Math.random() * window.innerHeight +
    "px";

    document.body.appendChild(
        dust
    );

    setTimeout(() => {

        dust.remove();

    }, 4000);
}


setInterval(
    createDust,
    300
);


// ==========================================
// BATTLE NOTIFICATION
// ==========================================

function battleAlert(message) {

    const alertBox =
    document.createElement("div");

    alertBox.classList.add(
        "battle-alert"
    );

    alertBox.innerText =
    message;

    document.body.appendChild(
        alertBox
    );

    setTimeout(() => {

        alertBox.remove();

    }, 2500);
}


// ==========================================
// RANDOM MATCH EVENTS
// ==========================================

const events = [

    "Enemy spotted!",
    "Airdrop landed!",
    "Zone shrinking!",
    "Squad revived!",
    "Vehicle detected!",
    "Sniper nearby!",
    "Loot acquired!"
];


function randomEvent() {

    let randomMessage =

    events[
        Math.floor(
            Math.random() *
            events.length
        )
    ];

    battleAlert(
        randomMessage
    );
}


setInterval(
    randomEvent,
    8000
);


// ==========================================
// PROBABILITY FLASH EFFECT
// ==========================================

function flashProbability() {

    const meter =
    document.querySelector(
        ".prob-card"
    );

    if (!meter) return;

    meter.style.transform =
    "scale(1.03)";

    setTimeout(() => {

        meter.style.transform =
        "scale(1)";

    }, 300);
}


setInterval(
    flashProbability,
    2500
);


// ==========================================
// LOADED
// ==========================================

console.log(
    "PUBG Animation Engine Loaded"
);