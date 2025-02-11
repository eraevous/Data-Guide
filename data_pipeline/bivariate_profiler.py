import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import entropy, gaussian_kde, pearsonr, spearmanr, kendalltau, chi2_contingency, f_oneway, pointbiserialr, ks_2samp, f_oneway
from statsmodels.graphics.mosaicplot import mosaic
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import LabelEncoder
from scipy.spatial.distance import euclidean
from sklearn.linear_model import LogisticRegression
from pandas.plotting import parallel_coordinates
from itertools import combinations
import geopandas as gpd
from esda.moran import Moran
from esda.geary import Geary
from sklearn.feature_selection import mutual_info_classif

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

    def compute_vif(self):
        """
        Compute Variance Inflation Factor (VIF) for detecting multicollinearity.
        """
        numeric_cols = self.df.select_dtypes(include=[np.number])
        vif_data = pd.DataFrame()
        vif_data["Variable"] = numeric_cols.columns
        vif_data["VIF"] = [variance_inflation_factor(numeric_cols.values, i) for i in range(numeric_cols.shape[1])]
        return vif_data

    def cramers_v(self, cat1, cat2):
        """
        Compute Cramér's V for categorical variables.
        """
        confusion_matrix = pd.crosstab(self.df[cat1], self.df[cat2])
        chi2 = chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        r, k = confusion_matrix.shape
        return np.sqrt(chi2 / (n * min(r - 1, k - 1)))

    def logistic_regression_effect(self, cat, num):
        """
        Fit a logistic regression model to test interaction effects.
        """
        le = LabelEncoder()
        y = le.fit_transform(self.df[cat])
        X = self.df[[num]].dropna()
        y = y[:len(X)]  # Ensure matching lengths
        model = LogisticRegression().fit(X, y)
        return {"coef": model.coef_[0][0], "intercept": model.intercept_[0]}

    def automated_bivariate_analysis(self):
        """
        Loop through all numeric-numeric, categorical-categorical, and numeric-categorical pairs.
        """
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns

        results = {}
        
        for num1, num2 in combinations(num_cols, 2):
            results[f"{num1}_vs_{num2}"] = self.correlation_analysis()
            self.scatter_plot(num1, num2)
        
        for cat1, cat2 in combinations(cat_cols, 2):
            results[f"{cat1}_vs_{cat2}"] = self.cramers_v(cat1, cat2)
            self.mosaic_plot(cat1, cat2)
        
        for num, cat in product(num_cols, cat_cols):
            results[f"{num}_by_{cat}"] = self.anova_test(num, cat)
            self.box_plot(num, cat)
        
        return results

    def parallel_coordinates_plot(self, class_column):
        """
        Generate a Parallel Coordinates plot for numeric variables grouped by a categorical variable.
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if class_column not in self.df.columns or class_column in numeric_cols:
            print(f"Invalid class column: {class_column}")
            return
        plt.figure(figsize=(12, 6))
        parallel_coordinates(self.df[numeric_cols.to_list() + [class_column]], class_column, colormap=plt.get_cmap("tab10"))
        plt.title("Parallel Coordinates Plot")
        plt.savefig(f"{self.output_dir}/parallel_coordinates.png")
        plt.close()

    def sankey_plot(self, cat1, cat2):
        """
        Generate a Sankey diagram for two categorical variables.
        """
        counts = self.df.groupby([cat1, cat2]).size().reset_index(name='count')
        labels = list(pd.concat([counts[cat1], counts[cat2]]).unique())
        source = counts[cat1].apply(lambda x: labels.index(x)).tolist()
        target = counts[cat2].apply(lambda x: labels.index(x)).tolist()
        
        fig = go.Figure(go.Sankey(
            node=dict(label=labels, pad=20, thickness=20),
            link=dict(source=source, target=target, value=counts['count'])
        ))
        fig.update_layout(title_text=f"Sankey Diagram: {cat1} → {cat2}")
        fig.write_image(f"{self.output_dir}/sankey_{cat1}_vs_{cat2}.png")

    def stacked_density_plot(self, numeric_col, category_col):
        """
        Generate a stacked density plot to see how a numeric variable varies by category.
        """
        categories = self.df[category_col].dropna().unique()
        plt.figure(figsize=(10, 6))
        for cat in categories:
            subset = self.df[self.df[category_col] == cat][numeric_col].dropna()
            density = gaussian_kde(subset)
            x_vals = np.linspace(subset.min(), subset.max(), 100)
            plt.plot(x_vals, density(x_vals), label=cat)
        plt.title(f"Stacked Density Plot: {numeric_col} by {category_col}")
        plt.xlabel(numeric_col)
        plt.ylabel("Density")
        plt.legend()
        plt.savefig(f"{self.output_dir}/stacked_density_{numeric_col}_by_{category_col}.png")
        plt.close()

    def hexbin_plot(self, x, y):
        """
        Generate a Hexbin plot for large datasets to visualize density.
        """
        plt.figure(figsize=(10, 6))
        plt.hexbin(self.df[x], self.df[y], gridsize=50, cmap="Blues", mincnt=1)
        plt.colorbar(label="Density")
        plt.title(f"Hexbin Plot: {x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(f"{self.output_dir}/hexbin_{x}_vs_{y}.png")
        plt.close()

    def pairplot(self):
        """
        Generate a Pairplot to visualize pairwise numeric relationships.
        """
        sns.pairplot(self.df)
        plt.savefig(f"{self.output_dir}/pairplot.png")
        plt.close()

    def point_biserial_corr(self, numeric_col, binary_col):
        """Compute Point-Biserial Correlation between a numeric and binary categorical variable."""
        return pointbiserialr(self.df[numeric_col], self.df[binary_col])[0]
    
    def tukey_hsd_test(self, numeric_col, category_col):
        """Perform Tukey’s HSD Test to find significant differences between categories."""
        groups = [group.dropna() for _, group in self.df.groupby(category_col)[numeric_col]]
        return f_oneway(*groups)
    
    def mutual_information(self, categorical_col, target_col):
        """Compute Mutual Information Score between categorical variables."""
        return mutual_info_classif(self.df[[categorical_col]], self.df[target_col], discrete_features=True)[0]
    
    def kolmogorov_smirnov_test(self, numeric_col, group_col):
        """Perform Kolmogorov-Smirnov test to compare distributions of two groups."""
        groups = self.df.groupby(group_col)[numeric_col].apply(lambda x: x.dropna().values)
        if len(groups) < 2:
            return None
        return ks_2samp(*groups[:2])
    
    def geary_moran_tests(self, geo_df, value_col):
        """Compute Geary’s C and Moran’s I for spatial autocorrelation."""
        w = geo_df.geometry.apply(lambda x: x.centroid).to_crs(epsg=3857)
        w_matrix = gpd.GeoDataFrame(geometry=w).distance_matrix()
        moran_i = Moran(geo_df[value_col].values, w_matrix)
        geary_c = Geary(geo_df[value_col].values, w_matrix)
        return {"Moran's I": moran_i.I, "Geary's C": geary_c.C}

    def bayesian_ab_test(self, category_col, metric_col, group_a, group_b):
        """
        Perform Bayesian A/B testing to compare two categorical groups.
        """
        data_a = self.df[self.df[category_col] == group_a][metric_col].dropna()
        data_b = self.df[self.df[category_col] == group_b][metric_col].dropna()
        
        with pm.Model() as model:
            mu_a = pm.Normal("mu_a", mu=np.mean(data_a), sigma=np.std(data_a))
            mu_b = pm.Normal("mu_b", mu=np.mean(data_b), sigma=np.std(data_b))
            diff = pm.Deterministic("difference", mu_b - mu_a)
            trace = pm.sample(2000, return_inferencedata=True)
        
        pm.plot_posterior(trace, var_names=["difference"])
        plt.title(f"Bayesian A/B Test: {group_a} vs {group_b}")
        plt.savefig(f"{self.output_dir}/bayesian_ab_{group_a}_vs_{group_b}.png")
        plt.close()
    
    def multidimensional_scaling(self, numeric_cols, n_components=2):
        """
        Perform Multidimensional Scaling (MDS) to visualize high-dimensional relationships.
        """
        mds = MDS(n_components=n_components, random_state=42)
        scaled_data = mds.fit_transform(self.df[numeric_cols].dropna())
        
        plt.figure(figsize=(10, 6))
        plt.scatter(scaled_data[:, 0], scaled_data[:, 1], alpha=0.7)
        plt.title("Multidimensional Scaling (MDS)")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.savefig(f"{self.output_dir}/mds_visualization.png")
        plt.close()
    
    def interaction_plot_analysis(self, category_col, numeric_col, group_col):
        """
        Generate an interaction plot to visualize relationships between variables.
        """
        plt.figure(figsize=(10, 6))
        interaction_plot(self.df[category_col], self.df[group_col], self.df[numeric_col], markers=['D', '^'], ms=8)
        plt.title(f"Interaction Plot: {numeric_col} by {category_col} and {group_col}")
        plt.savefig(f"{self.output_dir}/interaction_plot_{numeric_col}.png")
        plt.close()

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
    print(profiler.compute_vif())
