document.addEventListener("DOMContentLoaded", () => {
    const filter = document.getElementById("filter")
    if (filter == null) {
        throw Error("filter element not found")
    }
    const tbody = document.getElementById("ikea_offers")

    if (filter == null) {
        throw Error("table element not found")
    }

    const offers = Set()
    for (const row of tbody.children) {
        offers.add(row.lastChild.innerText)
    }
    for (let offer of offers) {
        const div = document.createElement("div")

        const input = document.createElement("input")
        input.type = "checkbox"
        input.name = offer + "check"

        const label = document.createElement("label")
        label.innerText = offer
        label.htmlFor = offer + "check"
        div.append([label, input])

        filter.appendChild(div)
    }
})