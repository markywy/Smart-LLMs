import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
plt.style.use("seaborn-v0_8-darkgrid")


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return pd.DataFrame([json.loads(line.strip()) for line in file])


def add_noise(x):
    if x == 0:
        return np.random.uniform(0, 0.05)
    elif x == 1:
        return 1 - np.random.uniform(0, 0.05)
    else:
        return x


def preprocess_data(en_df, zh_df, en_mapping, zh_mapping):
    def process_df(df, mapping):
        df["category"] = df["profession"].map(mapping)
        df["safe"] = pd.to_numeric(df["safe"], errors="coerce").apply(add_noise)
        df["completeness"] = pd.to_numeric(df["completeness"], errors="coerce").apply(
            add_noise
        )
        df["category"] = df["category"].astype("category")

        # Explode the 'applications' column
        df = df.explode("applications")

        # Rename 'applications' to 'application'
        df = df.rename(columns={"applications": "application"})

        df["application"] = df["application"].astype("category")

        return df

    en_df = process_df(en_df, en_mapping)
    zh_df = process_df(zh_df, zh_mapping)
    return en_df, zh_df


def plot_heatmap(combined_df):
    font_size, title_font_size, axis_label_size = 20, 24, 22

    pivot_count = pd.pivot_table(
        combined_df,
        values="safe",
        index="category",
        columns="application",
        aggfunc="count",
    )
    valid_apps = pivot_count.columns[pivot_count.sum() / len(pivot_count) >= 0.11]

    for score in ["safe", "completeness"]:
        pivot = pd.pivot_table(
            combined_df[combined_df["application"].isin(valid_apps)],
            values=score,
            index="category",
            columns="application",
            aggfunc="mean",
        )

        plt.figure(figsize=(20, 15))
        sns.heatmap(
            pivot,
            cmap="RdYlGn" if score == "safe" else "YlGnBu",
            annot=True,
            fmt=".2f",
            center=0.5 if score == "safe" else None,
            vmin=0,
            vmax=1,
            annot_kws={"size": 10},
        )

        plt.title(
            f"{score.capitalize()} Scores by Category and Application",
            fontsize=title_font_size,
        )
        plt.xlabel("Applications", fontsize=axis_label_size)
        plt.ylabel("Category", fontsize=axis_label_size)
        plt.xticks(rotation=45, ha="right", fontsize=font_size)
        plt.yticks(fontsize=font_size)

        plt.tight_layout()
        plt.savefig(f"{score}_heatmap_scores.png", dpi=300, bbox_inches="tight")
        plt.close()


def plot_grouped_boxplot(combined_df):
    font_size, title_font_size, axis_label_size = 20, 24, 22

    top_apps = (
        combined_df.groupby("application")
        .agg(
            {
                "safe": lambda x: x.max() - x.min(),
                "completeness": lambda x: x.max() - x.min(),
            }
        )
        .sum(axis=1)
        .nlargest(10)
        .index
    )

    plot_df = combined_df[combined_df["application"].isin(top_apps)]
    plot_df["Language"] = plot_df.index.map(
        lambda x: "English" if x < len(en_df) else "Chinese"
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 20))

    for ax, score in zip([ax1, ax2], ["safe", "completeness"]):
        sns.boxplot(x="application", y=score, hue="Language", data=plot_df, ax=ax)
        ax.set_title(
            f"{score.capitalize()} Scores by Language and Top Applications",
            fontsize=title_font_size,
        )
        ax.set_xticklabels(
            ax.get_xticklabels(), rotation=45, ha="right", fontsize=font_size
        )
        ax.set_xlabel("Applications", fontsize=axis_label_size)
        ax.set_ylabel(f"{score.capitalize()} Score", fontsize=axis_label_size)
        ax.tick_params(axis="y", labelsize=font_size)
        ax.legend(fontsize=font_size)
        ax.set_ylim(-0.1, 1.1)

    plt.tight_layout()
    plt.savefig("grouped_boxplot_scores.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_scatter_with_marginals(combined_df):
    font_size, title_font_size, label_font_size = 16, 20, 18

    # Add small random noise to spread out the points
    combined_df = combined_df.copy()
    combined_df["safe_jitter"] = combined_df["safe"] + np.random.normal(
        0, 0.02, len(combined_df)
    )
    combined_df["completeness_jitter"] = combined_df["completeness"] + np.random.normal(
        0, 0.02, len(combined_df)
    )

    # Clip values to ensure they stay within [0, 1]
    combined_df["safe_jitter"] = combined_df["safe_jitter"].clip(0, 1)
    combined_df["completeness_jitter"] = combined_df["completeness_jitter"].clip(0, 1)

    g = sns.JointGrid(
        data=combined_df, x="safe_jitter", y="completeness_jitter", height=16, ratio=4
    )

    # Plot points with increased transparency
    g.plot_joint(
        sns.scatterplot, data=combined_df, hue="category", alpha=0.1, s=30, legend=False
    )

    # Add a 2D kernel density estimate
    g.plot_joint(sns.kdeplot, cmap="YlGnBu", shade=True, alpha=0.5)

    g.plot_marginals(sns.kdeplot, fill=True, alpha=0.5)

    g.ax_joint.set_xlabel("Safe Score", fontsize=label_font_size)
    g.ax_joint.set_ylabel("Completeness Score", fontsize=label_font_size)
    g.ax_joint.tick_params(labelsize=font_size)

    # Set axis limits
    g.ax_joint.set_xlim(-0.05, 1.05)
    g.ax_joint.set_ylim(-0.05, 1.05)

    # Add diagonal line
    g.ax_joint.plot([0, 1], [0, 1], "r--", alpha=0.75, zorder=0)

    g.fig.suptitle(
        "Trade-off between Safe and Completeness Scores",
        y=1.02,
        fontsize=title_font_size,
    )

    # Move legend outside the plot
    legend = g.ax_joint.legend(
        title="Category",
        fontsize=font_size - 2,
        title_fontsize=font_size,
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )

    corr = combined_df["safe"].corr(combined_df["completeness"])
    g.ax_joint.text(
        0.05,
        0.95,
        f"Correlation: {corr:.2f}",
        transform=g.ax_joint.transAxes,
        fontsize=font_size,
        verticalalignment="top",
    )

    plt.tight_layout()
    plt.savefig("scatter_with_marginals.png", dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    base_dir = "./"
    en_df = load_data(f"{base_dir}/en_cleaned_data.jsonl")
    zh_df = load_data(f"{base_dir}/zh_cleaned_data.jsonl")
    en_mapping = load_json(f"{base_dir}/en_profession2cat.json")
    zh_mapping = load_json(f"{base_dir}/zh_profession2cat.json")

    en_df, zh_df = preprocess_data(en_df, zh_df, en_mapping, zh_mapping)
    combined_df = pd.concat([en_df, zh_df], ignore_index=True)

    if combined_df.empty:
        print("Combined dataframe is empty. Please check your data.")
    else:
        plot_heatmap(combined_df)
        plot_grouped_boxplot(combined_df)
        plot_scatter_with_marginals(combined_df)
        print("All plots have been generated and saved.")
