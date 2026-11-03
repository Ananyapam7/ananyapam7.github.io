(function () {
  var config = {
    responsive: true,
    displaylogo: false,
    displayModeBar: true,
    modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d", "toggleSpikelines"],
    toImageButtonOptions: { format: "svg", scale: 2 },
  };

  function reveal(spec) {
    document.querySelectorAll("[data-spline-plot]").forEach(function (el) {
      var figure = spec[el.getAttribute("data-spline-plot")];
      if (!figure || typeof Plotly === "undefined") {
        return;
      }
      el.hidden = false;
      Plotly.newPlot(el, figure.data, figure.layout, config).then(function () {
        var fallback = el.parentElement && el.parentElement.querySelector(".spline-fallback");
        if (fallback) {
          fallback.hidden = true;
        }
        Plotly.Plots.resize(el);
      });
    });
  }

  if (window.SPLINE_VI_PLOTS) {
    reveal(window.SPLINE_VI_PLOTS);
    return;
  }
  var url = window.SPLINE_VI_PLOT_URL;
  if (!url) {
    return;
  }
  fetch(url)
    .then(function (response) {
      if (!response.ok) {
        throw new Error(response.status);
      }
      return response.json();
    })
    .then(reveal)
    .catch(function () {
      /* The static figure remains visible when the interactive data cannot load. */
    });
})();
