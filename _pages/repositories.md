---
layout: page
permalink: /repositories/
title: Repositories
description: Codes released for some of my open source projects. Feel free to check them out.
nav: true
nav_order: 3
---

## GitHub stats

{% if site.data.repositories.github_users %}
<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for user in site.data.repositories.github_users %}
    {% include repository/repo_user.html username=user %}
  {% endfor %}
</div>
{% endif %}

### Contribution Graph

<img src="http://ghchart.rshah.org/Ananyapam7" alt="Ananyapam7's Github chart" />

---

## GitHub Repositories

Github repo links to some of my projects.

{% if site.data.repositories.github_repos %}
<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.html repository=repo %}
  {% endfor %}
</div>
{% endif %}

---

## Websites designed

These are some websites I developed during my undergrad days with [Satvik](https://sahasatvik.github.io/).

{% if site.data.repositories.websites_designed %}
<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for repo in site.data.repositories.websites_designed %}
    {% include repository/repo.html repository=repo %}
  {% endfor %}
</div>
{% endif %}