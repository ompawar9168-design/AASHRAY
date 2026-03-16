document.addEventListener("DOMContentLoaded", function () {
    console.log("AASHRAY JS loaded");

    const fileInput = document.getElementById("aadhaar_file");
    const fileName = document.getElementById("fileName");

    if (fileInput && fileName) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                fileName.textContent = fileInput.files[0].name;
            } else {
                fileName.textContent = "No file selected";
            }
        });
    }

    const callModal = document.getElementById("callModal");
    const receiveBtn = document.getElementById("receiveCallBtn");
    const dismissBtn = document.getElementById("dismissCallBtn");
    const callMedicineName = document.getElementById("callMedicineName");
    const spokenMessage = document.getElementById("spokenMessage");
    const callMessageBox = document.getElementById("callMessageBox");
    const familyReminderBox = document.getElementById("familyReminderBox");
    const familyAlertText = document.getElementById("familyAlertText");

    let activeReminderId = null;
    let modalOpen = false;
    let currentAudio = null;
    let ringtoneAudio = null;

    function stopRingtone() {
        if (ringtoneAudio) {
            ringtoneAudio.pause();
            ringtoneAudio.currentTime = 0;
            ringtoneAudio = null;
        }
    }

    function playRingtone() {
        stopRingtone();

        ringtoneAudio = new Audio("/static/audio/ringtone.mp3");
        ringtoneAudio.loop = true;

        ringtoneAudio.play().then(() => {
            console.log("Ringtone playing");
        }).catch((err) => {
            console.log("Ringtone failed", err);
        });
    }

    function stopCurrentAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }
    }

    function showCallModal(medicineName, message, familyName, familyPhone) {
        if (!callModal) return;

        if (callMedicineName) {
            callMedicineName.textContent = medicineName;
        }

        if (spokenMessage) {
            spokenMessage.textContent = message;
        }

        if (callMessageBox) {
            callMessageBox.classList.add("hidden");
        }

        if (familyReminderBox && familyAlertText) {
            if (familyName || familyPhone) {
                familyReminderBox.classList.remove("hidden");
                familyAlertText.textContent = `${familyName || "Family Member"} (${familyPhone || "No phone"}) will also get reminder`;
            } else {
                familyReminderBox.classList.add("hidden");
            }
        }

        callModal.classList.remove("hidden");
        modalOpen = true;

        playRingtone();

        if (navigator.vibrate) {
            navigator.vibrate([300, 200, 300, 200, 300]);
        }

        console.log("Call modal opened");
    }

    function hideCallModal() {
        if (!callModal) return;

        callModal.classList.add("hidden");
        modalOpen = false;
        activeReminderId = null;

        stopRingtone();
        stopCurrentAudio();

        console.log("Call modal closed");
    }

    async function markReminderDone() {
        if (!activeReminderId) return;

        try {
            await fetch(`/mark-reminder-alerted/${activeReminderId}`, {
                method: "POST"
            });
            console.log("Reminder marked done:", activeReminderId);
        } catch (e) {
            console.log("Reminder update failed", e);
        }
    }

    function playVoiceByLanguage(langCode, onComplete = null) {
        let audioPath = "/static/audio/en.mp3";

        if (langCode === "hi") {
            audioPath = "/static/audio/hi.mp3";
        } else if (langCode === "mr") {
            audioPath = "/static/audio/mr.mp3";
        }

        stopCurrentAudio();

        currentAudio = new Audio(audioPath);

        currentAudio.addEventListener("ended", function () {
            console.log("Voice completed");
            if (typeof onComplete === "function") {
                onComplete();
            }
        });

        currentAudio.addEventListener("error", function (err) {
            console.log("Voice audio error", err);
            if (typeof onComplete === "function") {
                onComplete();
            }
        });

        currentAudio.play().then(() => {
            console.log("Voice playing:", audioPath);
        }).catch((err) => {
            console.log("Voice play failed", err);
            if (typeof onComplete === "function") {
                onComplete();
            }
        });
    }

    async function checkDueReminder() {
        if (modalOpen) return;
        if (!callModal) return;

        try {
            const response = await fetch("/check-due-reminder", {
                cache: "no-store"
            });

            const data = await response.json();
            console.log("Reminder check:", data);

            if (data.due) {
                activeReminderId = data.id;
                showCallModal(
                    data.medicine_name,
                    data.message,
                    data.family_name,
                    data.family_phone
                );
            }
        } catch (e) {
            console.log("Reminder check failed", e);
        }
    }

    if (receiveBtn) {
        receiveBtn.addEventListener("click", async function () {
            stopRingtone();

            if (callMessageBox) {
                callMessageBox.classList.remove("hidden");
            }

            await markReminderDone();

            playVoiceByLanguage(window.currentLang || "en", function () {
                setTimeout(() => {
                    hideCallModal();
                }, 600);
            });
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener("click", async function () {
            await markReminderDone();
            hideCallModal();
        });
    }

    checkDueReminder();
    setInterval(checkDueReminder, 5000);
});