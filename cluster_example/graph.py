import matplotlib.pyplot as plt


xs = list(range(1, 16))
ys = [5, 5, 15, 15, 15, 5, 5, 5, 15, 15, 15, 5, 5, 5, 5]

print(len(xs))
print(len(ys))

fig, ax = plt.subplots()
ax: plt.Axes
ax.plot(xs, ys)
ax.scatter(xs, ys)
for x, y in zip (xs, ys):
    ax.text(x, y + .25, f"{x}", horizontalalignment="center", verticalalignment="bottom")
ax.set_ylim(3,17)
ax.set_yticks([])
ax.set_xticks([0, 5, 10, 15])
ax.set_ylabel("power")
ax.set_xlabel("time")
plt.show()