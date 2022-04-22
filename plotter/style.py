# plotter/style.py

import ROOT

colourdict = {
    'black':       ROOT.kBlack,
    'orange':      '#E24A33',
    'purple':      '#7A68A6',
    'blue':        '#348ABD',
    'lblue':       '#68add5',
    'turquoise':   '#188487',
    'red':         '#A60628',
    'pink':        '#CF4457',
    'green':       '#467821',
    'yellow':      '#e2a233',
    'lyellow':     '#f7fab3',
    'grey':        '#838283',
    'gray':        '#838283',
}

def get_color(c):

    if not isinstance(c, str):
        return c

    if c.startswith('#'):
        colour = ROOT.TColor.GetColor(c)
    else:
        try:
            colour = ROOT.TColor.GetColor(colourdict[c])
        except KeyError:
            if '+' in c:
                col, n = c.split('+')
                colour = getattr(ROOT, col)
                colour += int(n)
            elif '-' in c:
                col, n = c.split('-')
                colour = getattr(ROOT, col)
                colour -= int(n)
            else:
                colour = getattr(ROOT, c)

    return colour


def set_color(obj, color, fill=False, alpha=None):
    color = get_color(color)
    obj.SetLineColor(color)
    obj.SetMarkerColor(color)
    if fill:
        if alpha is not None:
            obj.SetFillColorAlpha(color, alpha)
        else:
            obj.SetFillColor(color)


def set_style(obj, color='kBlack'):

    # check if hist or graph
    is_hist  = obj.InheritsFrom('TH1')
    is_graph = obj.InheritsFrom('TGraph')

    # default
    obj.SetTitle('')
    if is_hist:
        obj.SetStats(0)
        obj.SetLineWidth(2)



    # color
    set_color(obj, color) #, fill, alpha)

def set_palette():
    s = array('d', [0.00, 0.34, 0.61, 0.84, 1.00])
    r = array('d', [0.00, 0.00, 0.87, 1.00, 0.51])
    g = array('d', [0.00, 0.81, 1.00, 0.20, 0.00])
    b = array('d', [0.51, 1.00, 0.12, 0.00, 0.00])
    ROOT.TColor.CreateGradientColorTable(len(s), s, r, g, b, 999)
    ROOT.gStyle.SetNumberContours(999)

def set_default_style():
    set_palette()
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetFrameFillColor(0)
    ROOT.gStyle.SetFrameBorderSize(0)
    ROOT.gStyle.SetFrameBorderMode(0)
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetTitleBorderSize(0)
    ROOT.gStyle.SetTitleFillColor(0)
    ROOT.gStyle.SetTextFont(42)
    ROOT.gStyle.SetLabelFont(42,"XY")
    ROOT.gStyle.SetTitleFont(42,"XY")
    ROOT.gStyle.SetEndErrorSize(0)

# colours
default_colours = [
    'black',
    'red',
    'blue',
    'green',
    'yellow',
    'orange',
]


# colours for the dict
colors = [
    '#E24A33',
    '#E24A33',
    '#32b45d',
    '#f7fab3',
    '#7A68A6',
    '#a4cee6',
    '#348ABD',
    '#348ABD',
    '#BCBC93',
    '#36BDBD',
    '#a4cee6',
    '#32b45d',
    ]

# plots configuration
class PlotConf(object):
    def __init__(self, xtitle, ytitle, legpos, xmin=None, xmax=None):
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.legpos = legpos
        self.xmin = xmin
        self.xmax = xmax

plots_conf = dict()
plots_conf['default'] = PlotConf('','', 'right')

plots_conf['cuts']            = PlotConf('', 'Events', 'right')
plots_conf['ph_n']            = PlotConf('Number of photons', 'Events', 'right')
plots_conf['el_n']            = PlotConf('Number of electrons', 'Events', 'right')
plots_conf['jet_n']           = PlotConf('Number of jets', 'Events', 'right')
plots_conf['ph_pt']           = PlotConf('p_{T}^{#gamma} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['ph_eta']          = PlotConf('Photon #eta', 'Events / (BIN GeV)', 'right')
plots_conf['ph_phi']          = PlotConf('Photon #phi', 'Events / (BIN GeV)', 'right')
plots_conf['ph_iso']          = PlotConf('E_{T}^{iso} [GeV]', 'Events (1/BIN GeV)', 'right')
plots_conf['met_et']          = PlotConf('E_{T}^{miss} [GeV]', 'Events / (BIN GeV)', 'right', 0, 500)
plots_conf['met_phi']         = PlotConf('#phi^{miss}', 'Events', 'right')
plots_conf['ht']              = PlotConf('H_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_pt']          = PlotConf('Jet p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_eta']         = PlotConf('Jet #eta', 'Events', 'right')
plots_conf['rt2']             = PlotConf('R_{T}^{2}', 'Events', 'left', 0.3, 1.1)
plots_conf['rt4']             = PlotConf('R_{T}^{4}', 'Events / BIN', 'left', 0.3, 1.05)

plots_conf['pt']  = PlotConf('p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['eta'] = PlotConf('#eta', 'Events / (BIN GeV)', 'right')
plots_conf['phi'] = PlotConf('#phi', 'Events / (BIN GeV)', 'right')
