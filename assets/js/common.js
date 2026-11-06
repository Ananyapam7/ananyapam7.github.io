$(document).ready(function() {
  // add toggle functionality to abstract and bibtex buttons
  $('a.abstract').click(function() {
    $(this).parent().parent().find(".abstract.hidden").toggleClass('open');
    $(this).parent().parent().find(".bibtex.hidden.open").toggleClass('open');
  });
  $('a.bibtex').click(function() {
    $(this).parent().parent().find(".bibtex.hidden").toggleClass('open');
    $(this).parent().parent().find(".abstract.hidden.open").toggleClass('open');
  });
  $('a').removeClass('waves-effect waves-light');

  // bootstrap-toc
  if($('#toc-sidebar').length){
    var navSelector = "#toc-sidebar";
    var $myNav = $(navSelector);
    Toc.init($myNav);
    $("body").scrollspy({
      target: navSelector,
    });
  }

  // Give same-origin notebook code the same palette as the surrounding page.
  function styleNotebook(iframe) {
    const notebook = iframe.contentDocument;
    const codeTheme = document.getElementById("code-theme");
    if (!notebook || !notebook.head || !notebook.body || !codeTheme) return;

    const styles = [
      ["notebook-layout", new URL("jupyter.css", codeTheme.href).href],
      ["code-theme", codeTheme.href]
    ];
    for (const [id, href] of styles) {
      if (!notebook.getElementById(id)) {
        const link = notebook.createElement("link");
        link.id = id;
        link.rel = "stylesheet";
        link.href = href;
        notebook.head.appendChild(link);
      }
    }
    const dark = document.documentElement.getAttribute("data-theme") === "dark";
    notebook.body.setAttribute("data-jp-theme-light", dark ? "false" : "true");
    notebook.body.setAttribute("data-jp-theme-name", dark ? "JupyterLab Dark" : "JupyterLab Light");
  }

  $('.jupyter-notebook-iframe-container iframe').each(function() {
    this.addEventListener("load", () => styleNotebook(this));
    if (this.contentDocument && this.contentDocument.readyState === "complete") {
      styleNotebook(this);
    }
  });
});

