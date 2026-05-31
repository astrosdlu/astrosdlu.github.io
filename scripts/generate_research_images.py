from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


OUT = Path("assets/research")
OUT.mkdir(parents=True, exist_ok=True)

BG = "#071517"
ORANGE = "#e8892f"
TEAL = "#0a6e69"
CREAM = "#f8f6ef"


def finish(fig, path):
    fig.savefig(OUT / path, dpi=220, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def add_label(ax, title, subtitle):
    ax.text(
        0.04,
        0.93,
        title,
        transform=ax.transAxes,
        color=CREAM,
        fontsize=13,
        fontweight="bold",
        ha="left",
        va="top",
    )
    ax.text(
        0.04,
        0.86,
        subtitle,
        transform=ax.transAxes,
        color=(1, 1, 1, 0.72),
        fontsize=8,
        ha="left",
        va="top",
    )


def galaxy_field():
    rng = np.random.default_rng(42)
    fig, ax = plt.subplots(figsize=(8.2, 5.1), facecolor=BG)
    ax.set_facecolor(BG)

    n = 1250
    x = rng.random(n)
    y = rng.random(n)
    size = rng.lognormal(mean=-0.2, sigma=0.75, size=n) * 9
    warm = rng.random(n)
    colors = np.column_stack(
        [
            0.35 + 0.55 * warm,
            0.45 + 0.28 * rng.random(n),
            0.72 + 0.23 * (1 - warm),
        ]
    )
    ax.scatter(x, y, s=size, c=colors, alpha=0.72, linewidths=0)

    for cx, cy, r, tilt in [
        (0.29, 0.57, 0.092, 18),
        (0.68, 0.35, 0.072, -28),
        (0.79, 0.71, 0.052, 40),
    ]:
        t = np.linspace(0, 5.6 * np.pi, 900)
        rr = r * (t / t.max()) ** 0.82
        xp = cx + rr * np.cos(t) * np.cos(np.deg2rad(tilt)) - 0.55 * rr * np.sin(t) * np.sin(np.deg2rad(tilt))
        yp = cy + rr * np.cos(t) * np.sin(np.deg2rad(tilt)) + 0.55 * rr * np.sin(t) * np.cos(np.deg2rad(tilt))
        ax.plot(xp, yp, color=(1.0, 0.72, 0.36, 0.55), lw=1.15)
        ax.scatter([cx], [cy], s=75, color="#fff4cc", edgecolor=ORANGE, linewidth=0.7)

    add_label(ax, "JWST-depth mock field", "synthetic high-redshift galaxy population")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish(fig, "jwst-mock-field.png")


def forward_modelling():
    rng = np.random.default_rng(7)
    fig = plt.figure(figsize=(8.2, 5.1), facecolor=BG)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.56], hspace=0.11, wspace=0.08)
    cmaps = [
        LinearSegmentedColormap.from_list("uv", ["#071517", "#173b57", "#73d4ff", "#ffffff"]),
        LinearSegmentedColormap.from_list("opt", ["#071517", "#503017", "#e8892f", "#fff0c2"]),
        LinearSegmentedColormap.from_list("submm", ["#071517", "#184f4d", "#4ae0b6", "#fff7d6"]),
    ]
    titles = ["far-UV", "optical", "sub-mm"]
    x = np.linspace(-1, 1, 280)
    y = np.linspace(-1, 1, 220)
    xx, yy = np.meshgrid(x, y)
    base = np.exp(-((xx / 0.58) ** 2 + (yy / 0.34) ** 2) * 2.4)
    clumps = sum(
        np.exp(-(((xx - rng.uniform(-0.42, 0.42)) / rng.uniform(0.04, 0.11)) ** 2 + ((yy - rng.uniform(-0.25, 0.25)) / rng.uniform(0.035, 0.09)) ** 2))
        for _ in range(16)
    )
    for i in range(3):
        ax = fig.add_subplot(gs[0, i])
        img = base * (0.55 + 0.25 * i) + clumps * (0.28 + 0.08 * i) + rng.normal(0, 0.035, base.shape)
        ax.imshow(img, origin="lower", cmap=cmaps[i], interpolation="bilinear")
        ax.text(0.06, 0.9, titles[i], transform=ax.transAxes, color=CREAM, fontsize=10, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    ax = fig.add_subplot(gs[1, :])
    lam = np.linspace(0.12, 850, 500)
    sed = (lam / 0.18) ** -1.7 * np.exp(-lam / 2.6) + 0.028 * np.exp(-((np.log10(lam) - 2.35) / 0.27) ** 2)
    sed += 0.004 * np.exp(-((np.log10(lam) - 0.7) / 0.18) ** 2)
    ax.plot(lam, sed, color=ORANGE, lw=2.2)
    ax.fill_between(lam, sed * 0.72, sed * 1.22, color=ORANGE, alpha=0.16, linewidth=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("observed wavelength", color=CREAM, fontsize=8)
    ax.set_ylabel("mock flux", color=CREAM, fontsize=8)
    ax.tick_params(colors=(1, 1, 1, 0.66), labelsize=7, length=2)
    for spine in ax.spines.values():
        spine.set_color((1, 1, 1, 0.22))
    ax.grid(color=(1, 1, 1, 0.08), lw=0.5)
    ax.set_facecolor("#0a181b")
    add_label(ax, "Radiative-transfer forward model", "image cubes + observable SED")
    finish(fig, "forward-modelling-mock.png")


def cgm_environment():
    rng = np.random.default_rng(11)
    fig, ax = plt.subplots(figsize=(8.2, 5.1), facecolor=BG)
    ax.set_facecolor(BG)
    n = 360
    x = np.linspace(-3, 3, n)
    y = np.linspace(-2, 2, n)
    xx, yy = np.meshgrid(x, y)
    field = np.zeros_like(xx)
    for _ in range(55):
        cx, cy = rng.normal(0, 1.25), rng.normal(0, 0.85)
        amp = rng.uniform(0.35, 1.1)
        sig = rng.uniform(0.08, 0.36)
        field += amp * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sig**2))
    field += 1.8 * np.exp(-(xx**2 + (yy / 0.7) ** 2) / 0.55)
    ax.imshow(field, origin="lower", extent=[-3, 3, -2, 2], cmap="magma", alpha=0.92)
    u = -yy / (xx**2 + yy**2 + 0.3) + 0.12 * np.cos(2 * yy)
    v = xx / (xx**2 + yy**2 + 0.3) + 0.08 * np.sin(2 * xx)
    ax.streamplot(x, y, u, v, color=(0.78, 0.96, 0.9, 0.48), linewidth=0.75, density=1.25, arrowsize=0.7)
    ax.contour(xx, yy, field, levels=7, colors=[(1, 1, 1, 0.25)], linewidths=0.55)
    ax.scatter([0], [0], s=150, color="#fff6cf", edgecolor=TEAL, linewidth=1.2)
    add_label(ax, "CGM angular-momentum environment", "synthetic density field with gas-flow streamlines")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish(fig, "cgm-angular-momentum.png")


def ifu_kinematics():
    fig, ax = plt.subplots(figsize=(8.2, 5.1), facecolor=BG)
    ax.set_facecolor(BG)
    n = 260
    x = np.linspace(-1.25, 1.25, n)
    y = np.linspace(-1.0, 1.0, n)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx**2 + (yy / 0.72) ** 2)
    theta = np.arctan2(yy / 0.72, xx)
    vel = 235 * np.tanh(2.8 * r) * np.cos(theta) * np.exp(-0.08 * r)
    mask = r > 1
    vel = np.ma.array(vel, mask=mask)
    im = ax.imshow(vel, origin="lower", extent=[-1.25, 1.25, -1.0, 1.0], cmap="RdBu_r", vmin=-240, vmax=240)
    ax.contour(xx, yy, np.ma.array(r, mask=mask), levels=np.linspace(0.2, 1.0, 5), colors=[(0, 0, 0, 0.28)], linewidths=0.7)
    ax.axhline(0, color=(1, 1, 1, 0.35), lw=0.8)
    ax.axvline(0, color=(1, 1, 1, 0.24), lw=0.8)
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.ax.tick_params(labelsize=7, colors=CREAM, length=2)
    cb.outline.set_edgecolor((1, 1, 1, 0.3))
    cb.set_label("line-of-sight velocity", color=CREAM, fontsize=8)
    add_label(ax, "IFU stellar kinematics", "MaNGA-style rotating velocity field")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish(fig, "ifu-kinematics.png")


if __name__ == "__main__":
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.linewidth": 0.8,
            "savefig.facecolor": BG,
        }
    )
    galaxy_field()
    forward_modelling()
    cgm_environment()
    ifu_kinematics()
