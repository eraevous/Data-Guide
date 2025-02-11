import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau, chi2_contingency, f_oneway

class BivariateProfiler:
    def __init__(self, dataframe, output_dir="bivariate_analysis"):
        self.df = dataframe
        self.output_dir = output_dir

    def correlation_analysis(self, method="pearson"):
        """
        Compute correlation matrix for numeric columns.
        Supported methods: Pearson, Spearman, Kendall.
        """
        corr_matrix = self.df.corr(method=method)
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title(f"{method.capitalize()} Correlation Matrix")
        plt.savefig(f"{self.output_dir}/correlation_matrix_{method}.png")
        plt.close()
        return corr_matrix

    def scatter_plot(self, x, y):
        """
        Generate scatter plot with regression line for numeric pairs.
        """
        plt.figure(figsize=(8, 6))
        sns.regplot(x=self.df[x], y=self.df[y], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
        plt.title(f"Scatter Plot: {x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(f"{self.output_dir}/scatter_{x}_vs_{y}.png")
        plt.close()

    def chi_square_test(self, cat1, cat2):
        """
        Perform Chi-Square test for two categorical variables.
        """
        contingency_table = pd.crosstab(self.df[cat1], self.df[cat2])
        chi2, p, _, _ = chi2_contingency(contingency_table)
        return {"chi2": chi2, "p_value": p}

    def mosaic_plot(self, cat1, cat2):
        """
        Generate a mosaic plot for categorical variable relationships.
        """
        from statsmodels.graphics.mosaicplot import mosaic
        plt.figure(figsize=(10, 6))
        mosaic(self.df, [cat1, cat2])
        plt.title(f"Mosaic Plot: {cat1} vs {cat2}")
        plt.savefig(f"{self.output_dir}/mosaic_{cat1}_vs_{cat2}.png")
        plt.close()

    def box_plot(self, num, cat):
        """
        Generate a box plot for a numeric variable across categorical groups.
        """
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=self.df[cat], y=self.df[num])
        plt.title(f"Box Plot: {num} by {cat}")
        plt.savefig(f"{self.output_dir}/boxplot_{num}_by_{cat}.png")
        plt.close()

    def anova_test(self, num, cat):
        """
        Perform ANOVA (F-test) to test numeric variable differences across categorical groups.
        """
        groups = [self.df[self.df[cat] == level][num] for level in self.df[cat].unique()]
        f_stat, p_value = f_oneway(*groups)
        return {"f_stat": f_stat, "p_value": p_value}

# Example Usage
if __name__ == "__main__":
    df = sns.load_dataset("titanic").dropna()
    profiler = BivariateProfiler(df)
    print(profiler.correlation_analysis("pearson"))
    profiler.scatter_plot("age", "fare")
    print(profiler.chi_square_test("sex", "class"))
    profiler.mosaic_plot("sex", "class")
    profiler.box_plot("fare", "class")
    print(profiler.anova_test("fare", "class"))
