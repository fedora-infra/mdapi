const ttls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tpls = [...ttls].map(ttel => new bootstrap.Tooltip(ttel, { customClass: "bg-body-secondary tltp" }));

function navigate(event, srce, name) {
    event.preventDefault();
    const srcedata = document.getElementById(srce).innerText;
    const namedata = document.getElementById(name).value;
    if (namedata.trim() !== "") {
        const link = srcedata + namedata;
        window.open(link, "_blank");
    }
}

function copylink(srce, name) {
    const srcedata = document.getElementById(srce).innerText;
    const namedata = document.getElementById(name).value;
    const link = srcedata + namedata;
    try {
        navigator.clipboard.writeText(link).then(
            () => {
                const copydone = document.getElementById("copydone");
                const doneelem = new bootstrap.Toast(copydone);
                doneelem.show();
            }).catch(expt => {
                const copyfail = document.getElementById("copyfail");
                const failelem = new bootstrap.Toast(copyfail);
                failelem.show();
            }
        );
    } catch (expt) {
        const copyfail = document.getElementById("copyfail");
        const failelem = new bootstrap.Toast(copyfail);
        failelem.show();
    }
}