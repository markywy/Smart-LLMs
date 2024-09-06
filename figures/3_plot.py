import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from scipy.stats import pearsonr

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


def plot_heatmap(df, lang_prefix):
    font_size, title_font_size, axis_label_size = 20, 24, 22

    pivot_count = pd.pivot_table(
        df,
        values="safe",
        index="category",
        columns="application",
        aggfunc="count",
    )
    valid_apps = pivot_count.columns[pivot_count.sum() / len(pivot_count) >= 0.11]

    for score in ["safe", "completeness"]:
        pivot = pd.pivot_table(
            df[df["application"].isin(valid_apps)],
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
            f"{score.capitalize()} Scores by Category and Application ({lang_prefix.upper()})",
            fontsize=title_font_size,
        )
        plt.xlabel("Applications", fontsize=axis_label_size)
        plt.ylabel("Category", fontsize=axis_label_size)
        plt.xticks(rotation=45, ha="right", fontsize=font_size)
        plt.yticks(fontsize=font_size)

        plt.tight_layout()
        plt.savefig(
            f"{lang_prefix}_{score}_heatmap_scores.png", dpi=300, bbox_inches="tight"
        )
        plt.close()


def plot_grouped_boxplot(df, lang_prefix):
    font_size, title_font_size, axis_label_size = 20, 24, 22

    top_apps = (
        df.groupby("application")
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

    plot_df = df[df["application"].isin(top_apps)]

    if lang_prefix == "combined":
        plot_df["Language"] = plot_df.index.map(
            lambda x: "English" if x < len(en_df) else "Chinese"
        )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 20))

    for ax, score in zip([ax1, ax2], ["safe", "completeness"]):
        if lang_prefix == "combined":
            sns.boxplot(x="application", y=score, hue="Language", data=plot_df, ax=ax)
        else:
            sns.boxplot(x="application", y=score, data=plot_df, ax=ax)

        ax.set_title(
            f"{score.capitalize()} Scores by Top Applications ({lang_prefix.upper()})",
            fontsize=title_font_size,
        )
        ax.set_xticklabels(
            ax.get_xticklabels(), rotation=45, ha="right", fontsize=font_size
        )
        ax.set_xlabel("Applications", fontsize=axis_label_size)
        ax.set_ylabel(f"{score.capitalize()} Score", fontsize=axis_label_size)
        ax.tick_params(axis="y", labelsize=font_size)
        ax.set_ylim(-0.1, 1.1)

        if lang_prefix == "combined":
            ax.legend(fontsize=font_size)

    plt.tight_layout()
    plt.savefig(
        f"{lang_prefix}_grouped_boxplot_scores.png", dpi=300, bbox_inches="tight"
    )
    plt.close()


def plot_scatter_with_marginals(df, lang_prefix):
    font_size, title_font_size, label_font_size = 16, 20, 18

    # Add small random noise to spread out the points
    df = df.copy()
    df["safe_jitter"] = df["safe"] + np.random.normal(0, 0.02, len(df))
    df["completeness_jitter"] = df["completeness"] + np.random.normal(0, 0.02, len(df))

    # Clip values to ensure they stay within [0, 1]
    df["safe_jitter"] = df["safe_jitter"].clip(0, 1)
    df["completeness_jitter"] = df["completeness_jitter"].clip(0, 1)

    if lang_prefix == "combined":
        df["Language"] = df.index.map(
            lambda x: "English" if x < len(en_df) else "Chinese"
        )

    g = sns.JointGrid(
        data=df, x="safe_jitter", y="completeness_jitter", height=16, ratio=4
    )

    # Plot points with increased transparency
    if lang_prefix == "combined":
        g.plot_joint(
            sns.scatterplot, data=df, hue="Language", style="category", alpha=0.3, s=30
        )
    else:
        g.plot_joint(sns.scatterplot, data=df, hue="category", alpha=0.3, s=30)

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
        f"Trade-off between Safe and Completeness Scores ({lang_prefix.upper()})",
        y=1.02,
        fontsize=title_font_size,
    )

    # Move legend outside the plot
    if lang_prefix == "combined":
        handles, labels = g.ax_joint.get_legend_handles_labels()
        language_legend = g.ax_joint.legend(
            handles[:2],
            labels[:2],
            title="Language",
            fontsize=font_size - 2,
            title_fontsize=font_size,
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )
        g.ax_joint.add_artist(language_legend)
        category_legend = g.ax_joint.legend(
            handles[2:],
            labels[2:],
            title="Category",
            fontsize=font_size - 2,
            title_fontsize=font_size,
            bbox_to_anchor=(1.05, 0.5),
            loc="center left",
        )
    else:
        g.ax_joint.legend(
            title="Category",
            fontsize=font_size - 2,
            title_fontsize=font_size,
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )

    corr = df["safe"].corr(df["completeness"])
    g.ax_joint.text(
        0.05,
        0.95,
        f"Correlation: {corr:.2f}",
        transform=g.ax_joint.transAxes,
        fontsize=font_size,
        verticalalignment="top",
    )

    plt.tight_layout()
    plt.savefig(
        f"{lang_prefix}_scatter_with_marginals.png", dpi=300, bbox_inches="tight"
    )
    plt.close()


import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch


def plot_score_distribution(df, lang_prefix, n_top=10):
    font_size, title_font_size, axis_label_size = 12, 16, 14
    safety_color = 'royalblue'
    completeness_color = 'limegreen'

    # Function to select diverse professions based on safety scores
    def select_diverse_professions(df, n):
        sorted_profs = df.groupby("profession")["safe"].mean().sort_values()
        step = len(sorted_profs) // n
        return [sorted_profs.index[i] for i in range(0, len(sorted_profs), step)][:n]

    # Select diverse professions
    diverse_profs = select_diverse_professions(df, n_top)
    plot_df_prof = df[df["profession"].isin(diverse_profs)]

    # Create subplots for professions and applications
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 24))

    # Plot for professions
    sns.boxenplot(x="profession", y="safe", data=plot_df_prof, ax=ax1, color=safety_color)
    sns.boxenplot(x="profession", y="completeness", data=plot_df_prof, ax=ax1, color=completeness_color)

    ax1.set_title(
        f"Distribution of Scores by Profession ({lang_prefix.upper()})",
        fontsize=title_font_size,
    )
    ax1.set_xlabel("Profession", fontsize=axis_label_size)
    ax1.set_ylabel("Score", fontsize=axis_label_size)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", fontsize=font_size)
    ax1.tick_params(axis="y", labelsize=font_size)

    # Create custom legend
    legend_elements = [Patch(facecolor=safety_color, edgecolor='black', label='Safety'),
                       Patch(facecolor=completeness_color, edgecolor='black', label='Completeness')]
    ax1.legend(handles=legend_elements, fontsize=font_size, loc='upper right')

    # Select top applications based on usage, excluding all-zero scores
    top_apps = df.groupby('application', observed=True).agg({
        'safe': lambda x: (x.sum() > 0) | (x.count() == 0),
        'completeness': lambda x: (x.sum() > 0) | (x.count() == 0),
    })
    top_apps['count'] = df.groupby('application', observed=True).size()
    top_apps = top_apps[(top_apps['safe'] | top_apps['completeness']) & (top_apps['count'] > 0)]
    top_apps = top_apps.sort_values('count', ascending=False).head(n_top).index

    plot_df_app = df[df['application'].isin(top_apps)]

    # Calculate mean scores for applications
    mean_scores = plot_df_app.groupby('application').agg({
        'safe': 'mean',
        'completeness': 'mean'
    }).reset_index()

    # Plot for applications
    x = range(len(mean_scores))
    width = 0.35
    ax2.bar([i - width/2 for i in x], mean_scores['safe'], width, color=safety_color, alpha=0.7, label='Safety')
    ax2.bar([i + width/2 for i in x], mean_scores['completeness'], width, color=completeness_color, alpha=0.7, label='Completeness')

    ax2.set_title(
        f"Mean Scores by Top Applications ({lang_prefix.upper()})",
        fontsize=title_font_size,
    )
    ax2.set_xlabel("Application", fontsize=axis_label_size)
    ax2.set_ylabel("Mean Score", fontsize=axis_label_size)
    ax2.set_xticks(x)
    ax2.set_xticklabels(mean_scores['application'], rotation=45, ha="right", fontsize=font_size)
    ax2.tick_params(axis="y", labelsize=font_size)
    ax2.legend(fontsize=font_size, loc='upper right')

    # Check for applications with all zero scores
    def check_zero_scores(df):
        zero_scores = df.groupby('application').agg({
            'safe': lambda x: (x == 0).all(),
            'completeness': lambda x: (x == 0).all(),
        })
        zero_scores['count'] = df.groupby('application').size()
        return zero_scores[zero_scores['safe'] & zero_scores['completeness']]

    zero_score_apps = check_zero_scores(df)
    if not zero_score_apps.empty:
        ax2.text(0.05, 0.95, f"Note: {len(zero_score_apps)} applications have all zero scores", 
                 transform=ax2.transAxes, fontsize=10, verticalalignment='top')

    plt.tight_layout()
    plt.savefig(f"{lang_prefix}_score_distribution.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_profession_score_relationship(df, lang_prefix):
    plt.figure(figsize=(16, 12))
    font_size, title_font_size, axis_label_size = 12, 18, 14

    # Calculate mean scores for each profession
    prof_scores = (
        df.groupby("profession")
        .agg({"safe": "mean", "completeness": "mean"})
        .reset_index()
    )

    # Calculate correlation
    corr, _ = pearsonr(prof_scores["safe"], prof_scores["completeness"])

    # Create scatter plot
    scatter = plt.scatter(
        prof_scores["safe"],
        prof_scores["completeness"],
        c=prof_scores["safe"] + prof_scores["completeness"],
        cmap="viridis",
        alpha=0.7,
        s=100,
    )

    # Add labels for some interesting points
    for i, row in prof_scores.iterrows():
        if (
            (row["safe"] < 0.2 and row["completeness"] > 0.8)
            or (row["safe"] > 0.8 and row["completeness"] < 0.2)
            or (row["safe"] > 0.8 and row["completeness"] > 0.8)
        ):
            plt.annotate(
                row["profession"],
                (row["safe"], row["completeness"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
            )

    # Customize the plot
    plt.title(
        f"Relationship between Safety and Completeness Scores by Profession ({lang_prefix.upper()})",
        fontsize=title_font_size,
    )
    plt.xlabel("Safety Score", fontsize=axis_label_size)
    plt.ylabel("Completeness Score", fontsize=axis_label_size)
    plt.tick_params(axis="both", which="major", labelsize=font_size)

    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label("Combined Score (Safety + Completeness)", fontsize=axis_label_size)
    cbar.ax.tick_params(labelsize=font_size)

    # Add correlation coefficient
    plt.text(
        0.05,
        0.95,
        f"Correlation: {corr:.2f}",
        transform=plt.gca().transAxes,
        fontsize=font_size,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.8),
    )

    # Add trend line
    z = np.polyfit(prof_scores["safe"], prof_scores["completeness"], 1)
    p = np.poly1d(z)
    plt.plot(prof_scores["safe"], p(prof_scores["safe"]), "r--", alpha=0.8)

    # Set axis limits
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)

    # Add grid
    plt.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(
        f"{lang_prefix}_profession_score_relationship.png", dpi=300, bbox_inches="tight"
    )
    plt.close()


def plot_profession_score_distributions(df, lang_prefix, top_n=10):
    plt.figure(figsize=(20, 12))
    font_size, title_font_size, axis_label_size = 12, 18, 14

    # Select top N professions by number of entries
    top_professions = df["profession"].value_counts().nlargest(top_n).index

    # Prepare data for plotting
    plot_data = df[df["profession"].isin(top_professions)].melt(
        id_vars=["profession"],
        value_vars=["safe", "completeness"],
        var_name="Score Type",
        value_name="Score",
    )

    # Create violin plot
    sns.violinplot(
        x="profession",
        y="Score",
        hue="Score Type",
        data=plot_data,
        split=True,
        inner="quartile",
        cut=0,
        scale="width",
    )

    # Customize the plot
    plt.title(
        f"Distribution of Safety and Completeness Scores by Top {top_n} Professions ({lang_prefix.upper()})",
        fontsize=title_font_size,
    )
    plt.xlabel("Profession", fontsize=axis_label_size)
    plt.ylabel("Score", fontsize=axis_label_size)
    plt.xticks(rotation=45, ha="right", fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.legend(title="Score Type", fontsize=font_size, title_fontsize=font_size)

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(
        f"{lang_prefix}_profession_score_distributions.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def generate_plots(df, lang_prefix):
    plot_heatmap(df, lang_prefix)
    plot_grouped_boxplot(df, lang_prefix)
    plot_scatter_with_marginals(df, lang_prefix)
    plot_score_distribution(df, lang_prefix)
    plot_profession_score_relationship(df, lang_prefix)
    plot_profession_score_distributions(df, lang_prefix)


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
        # Generate plots for English data
        generate_plots(en_df, "en")

        # Generate plots for Chinese data
        generate_plots(zh_df, "zh")

        # Generate plots for combined data
        generate_plots(combined_df, "combined")

        print("All plots have been generated and saved.")
