---
layout: post
title: "How a Rolling Circle Draws a Straight Line"
date: 2026-08-23 12:00:00 +0200
description: "Roll a circle inside one twice its size and every point on its rim traces a diameter. An interactive look at the geometry and the simple harmonic motion behind it."
tags: math
thumbnail: /assets/img/rolling-circles/geometry.svg
---

Watch the orange dot. The small circle rolls around the inside of the larger one, yet the dot slides back and forth along the same straight line. Pick a different point on the rim and the line turns, but it still passes through the center.

{% include rolling-circle-demo.html %}

## Why the two angles turn at the same rate

Fix a circle of radius $$2r$$ with center $$C$$. Inside it, roll a circle of radius $$r$$ with center $$A$$. Because the circles touch internally, $$A$$ stays a distance $$2r-r=r$$ from $$C$$. Let $$\phi=\Omega t$$ be the counterclockwise angle of $$CA$$, measured from the horizontal.

<figure>
  <img class="img-fluid rounded d-block mx-auto" src="{{ '/assets/img/rolling-circles/geometry.svg' | relative_url }}" width="640" height="360" alt="A smaller circle touches the inside of a circle twice its radius at T. C is the fixed center, A is the rolling center, and P lies on a diameter through C.">
  <figcaption class="caption">The center A is halfway from C to the contact point T. The orange line is the diameter traced by P.</figcaption>
</figure>

At the contact point $$T$$, the moving circle touches a stationary wall. With no slipping, the velocity of the bit of rim at $$T$$ must be zero. The center carries it forward at speed $$r\Omega$$, while the circle's spin carries it backward at speed $$r\lvert\omega\rvert$$. The two cancel, so the **signed** angular velocity of the small circle is $$\omega=-\Omega$$. Its center goes counterclockwise while the circle itself turns clockwise at the same rate.

## Where the straight line comes from

Mark a point $$P$$ on the rim. At $$t=0$$, let $$\theta$$ be the angle of $$AP$$ from the horizontal. At time $$t$$, the two vectors that take us from $$C$$ to $$P$$ are

$$
\overrightarrow{CA}=r\begin{pmatrix}\cos\phi\\\sin\phi\end{pmatrix},
\qquad
\overrightarrow{AP}=r\begin{pmatrix}\cos(\theta-\phi)\\\sin(\theta-\phi)\end{pmatrix}.
$$

The vectors have the same length, and their angles always add up to $$\theta$$. Relative to the direction $$\alpha=\theta/2$$, one makes an angle $$\phi-\alpha$$ and the other makes its negative. So their perpendicular components cancel, and their components along that direction add. Equivalently, the sum-to-product identities give

$$
\overrightarrow{CP}
=2r\cos\!\left(\phi-\frac{\theta}{2}\right)
\begin{pmatrix}\cos(\theta/2)\\\sin(\theta/2)\end{pmatrix}.
$$

Only the cosine changes with time. A positive value puts the point on one side of $$C$$, a negative value puts it on the other, and zero puts it right at the center. That is the whole diameter. Try changing the rim angle in the animation. Moving the mark by $$60^\circ$$ turns its line by $$30^\circ$$.

## What the motion feels like along the line

Imagine standing on the diameter and measuring the dot's signed position $$s$$ along it. You would see

$$
s(t)=2r\cos\!\left(\Omega t-\frac{\theta}{2}\right),
\qquad
\ddot{s}=-\Omega^2s.
$$

This is simple harmonic motion. The amplitude is $$2r$$, the **radius** of the fixed circle, and the full trip from one endpoint to the other spans $$4r$$. The point slows to a stop at each end, then passes through the center at its highest speed. The graph above shows that rhythm over one revolution.

The ratio of radii does two jobs at once. It makes the orbit of $$A$$ and the radius $$AP$$ the same length, and it makes their angles turn at equal rates in opposite directions. A point at $$\theta=0$$ traces the horizontal diameter. One on the opposite side of the small circle, at $$\theta=\pi$$, traces the vertical diameter. Everything in between follows the same rule.
