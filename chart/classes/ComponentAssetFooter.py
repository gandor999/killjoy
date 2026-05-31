import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import simpledialog
from matplotlib.patches import FancyBboxPatch

class ComponentAssetFooter:
    def __init__(self, fig, tickers, on_refresh_callback=None):
        """
        Manages an interactive asset management bar pinned explicitly at the 
        absolute bottom margin of the window, safely below all axis text.
        """
        self.fig = fig
        self.tickers = tickers
        self.on_refresh_callback = on_refresh_callback
        
        self.footer_ax = None
        self.ax_add = None
        self.ax_remove = None
        self.btn_add = None
        self.btn_remove = None

        self.render_ui()

    def render_ui(self):
        """Clears and renders the bottom control ribbon at fixed window coordinates."""
        self.clear_ui()

        # 1. Background Gray Ribbon [left, bottom, width, height]
        # Pinned at absolute bottom (0.02) across the entire chart span (0.12 to 0.65)
        self.footer_ax = self.fig.add_axes([0.12, 0.02, 0.53, 0.045])
        self.footer_ax.axis("off")
        
        rect = FancyBboxPatch(
            (0, 0), 1, 1, transform=self.footer_ax.transAxes,
            fc="#f7f7f7", ec="#e0e0e0", lw=1.2, boxstyle="round,pad=0.01"
        )
        self.footer_ax.add_patch(rect)

        ticker_string = "Component Assets:  " + ("   •   ".join([str(t) for t in self.tickers]) if self.tickers else "Empty Basket")
        self.footer_ax.text(
            0.02, 0.5, ticker_string, transform=self.footer_ax.transAxes,
            fontsize=9.5, fontweight="bold", fontname="Arial", color="#555555",
            va="center", ha="left"
        )

        # 2. Add Button (Floating further right, perfectly aligned at bottom 0.02)
        self.ax_add = self.fig.add_axes([0.67, 0.02, 0.10, 0.045])
        self.btn_add = Button(self.ax_add, '+ Add', color='#e1f5fe', hovercolor='#b3e5fc')
        self.btn_add.label.set_fontsize(9.5)
        self.btn_add.label.set_weight('bold')
        self.btn_add.on_clicked(self._add_ticker_action)

        # 3. Remove Button
        self.ax_remove = self.fig.add_axes([0.78, 0.02, 0.10, 0.045])
        self.btn_remove = Button(self.ax_remove, '- Remove', color='#ffebee', hovercolor='#ffcdd2')
        self.btn_remove.label.set_fontsize(9.5)
        self.btn_remove.label.set_weight('bold')
        self.btn_remove.on_clicked(self._remove_ticker_action)

    def _add_ticker_action(self, event):
        root = tk.Tk()
        root.withdraw()
        new_ticker = simpledialog.askstring("Add Asset", "Enter Stock Ticker Symbol:")
        root.destroy()
        if new_ticker:
            clean_ticker = new_ticker.strip().upper()
            if clean_ticker not in self.tickers:
                self.tickers.append(clean_ticker)
                self.render_ui()
                if self.on_refresh_callback: self.on_refresh_callback()

    def _remove_ticker_action(self, event):
        if not self.tickers: return
        root = tk.Tk()
        root.withdraw()
        target_ticker = simpledialog.askstring("Remove Asset", f"Current: {', '.join(self.tickers)}")
        root.destroy()
        if target_ticker:
            clean_ticker = target_ticker.strip().upper()
            if clean_ticker in self.tickers:
                self.tickers.remove(clean_ticker)
                self.render_ui()
                if self.on_refresh_callback: self.on_refresh_callback()

    def clear_ui(self):
        for ax in [self.footer_ax, self.ax_add, self.ax_remove]:
            if ax is not None:
                try: ax.remove()
                except KeyError: pass
        self.footer_ax = self.ax_add = self.ax_remove = None