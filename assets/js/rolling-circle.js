(function () {
  "use strict";

  var demo = document.querySelector("[data-rolling-circle]");
  if (!demo) return;

  function element(name) {
    return demo.querySelector("[data-" + name + "]");
  }

  function attributes(node, values) {
    Object.keys(values).forEach(function (name) {
      node.setAttribute(name, values[name]);
    });
  }

  function svgElement(name, className) {
    var node = document.createElementNS("http://www.w3.org/2000/svg", name);
    node.setAttribute("class", className);
    return node;
  }

  var origin = { x: 200, y: 175 };
  var radius = 72;
  var radians = Math.PI / 180;
  var defaultAngle = 60;
  var phase = defaultAngle;
  var rim = defaultAngle;
  var frame = null;
  var lastTime = null;

  var wheel = element("wheel");
  var centerMarker = element("center");
  var contactMarker = element("contact");
  var track = element("track");
  var orbitArm = element("orbit-arm");
  var pointArm = element("point-arm");
  var dot = element("dot");
  var centerLabel = element("center-label");
  var dotLabel = element("dot-label");
  var wave = element("wave");
  var cursor = element("cursor");
  var graphDot = element("graph-dot");
  var extra = element("extra");
  var play = element("play");
  var more = element("more");
  var phaseInput = element("phase");
  var rimInput = element("rim");
  var phaseValue = element("phase-value");
  var rimValue = element("rim-value");

  var otherPoints = [45, 90, 135, 180, 225, 270, 315].map(function (offset) {
    var line = svgElement("line", "rolling-circle__extra-line");
    var marker = svgElement("circle", "rolling-circle__extra-dot");
    marker.setAttribute("r", 4.5);
    extra.appendChild(line);
    extra.appendChild(marker);
    return { offset: offset, line: line, marker: marker };
  });

  function offset(point, length, angle) {
    return {
      x: point.x + length * Math.cos(angle * radians),
      y: point.y - length * Math.sin(angle * radians)
    };
  }

  function segment(node, first, second) {
    attributes(node, { x1: first.x, y1: first.y, x2: second.x, y2: second.y });
  }

  function place(node, point) {
    attributes(node, { cx: point.x, cy: point.y });
  }

  function diameter(node, initialAngle) {
    segment(node, offset(origin, -2 * radius, initialAngle / 2),
      offset(origin, 2 * radius, initialAngle / 2));
  }

  function graphPosition(angle) {
    return {
      x: 48 + 281 * angle / 360,
      y: 97 - 60 * Math.cos((angle - rim / 2) * radians)
    };
  }

  function drawWave() {
    var path = [];
    for (var angle = 0; angle <= 360; angle += 4) {
      var point = graphPosition(angle);
      path.push((angle === 0 ? "M" : "L") + point.x.toFixed(2) + " " + point.y.toFixed(2));
    }
    wave.setAttribute("d", path.join(" "));
  }

  function draw() {
    var center = offset(origin, radius, phase);
    var point = offset(center, radius, rim - phase);
    place(wheel, center);
    place(centerMarker, center);
    place(contactMarker, offset(origin, 2 * radius, phase));
    place(dot, point);
    segment(orbitArm, origin, center);
    segment(pointArm, center, point);
    attributes(centerLabel, { x: center.x - 14, y: center.y - 8 });
    attributes(dotLabel, { x: point.x + 11, y: point.y - 7 });
    diameter(track, rim);

    extra.style.display = more.checked ? "" : "none";
    if (more.checked) {
      otherPoints.forEach(function (entry) {
        var angle = rim + entry.offset;
        diameter(entry.line, angle);
        place(entry.marker, offset(center, radius, angle - phase));
      });
    }

    var plotPoint = graphPosition(phase);
    attributes(cursor, { x1: plotPoint.x, x2: plotPoint.x });
    place(graphDot, plotPoint);
    phaseInput.value = Math.round(phase);
    phaseValue.textContent = phaseInput.value + "°";
    rimValue.textContent = rim + "°";
  }

  function pause() {
    if (frame !== null) window.cancelAnimationFrame(frame);
    frame = null;
    lastTime = null;
    play.textContent = "Play";
  }

  function tick(time) {
    if (lastTime !== null) phase = (phase + (time - lastTime) * 0.045) % 360;
    lastTime = time;
    draw();
    frame = window.requestAnimationFrame(tick);
  }

  play.addEventListener("click", function () {
    if (frame !== null) {
      pause();
      return;
    }
    play.textContent = "Pause";
    frame = window.requestAnimationFrame(tick);
  });

  element("reset").addEventListener("click", function () {
    pause();
    phase = defaultAngle;
    rim = defaultAngle;
    rimInput.value = rim;
    more.checked = more.defaultChecked;
    drawWave();
    draw();
  });

  phaseInput.addEventListener("input", function () {
    pause();
    phase = Number(phaseInput.value);
    draw();
  });

  rimInput.addEventListener("input", function () {
    rim = Number(rimInput.value);
    drawWave();
    draw();
  });

  more.addEventListener("change", draw);

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) pause();
  });

  drawWave();
  draw();
  element("controls").hidden = false;
})();
