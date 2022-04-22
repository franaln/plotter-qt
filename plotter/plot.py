# plotter
# plot.py

import ROOT

from PySide2.QtCore import QModelIndex, Qt, QAbstractItemModel, Signal

from plotter.style import *


class Plot:

    number_of_plot = 0

    def __init__(self):

        self.name = 'plot_%d' % Plot.number_of_plot

        self.canvas = None
        self.legend = None

        self.xmin = 0
        self.xmax = 100
        self.ymin = 0
        self.ymax = 100
        self.zmin = 0
        self.zmax = 100

        self.objects  = []
        self.labels   = []
        self.opts = []

        self.logx = False
        self.logy = False
        self.logz = False

        Plot.number_of_plot = Plot.number_of_plot + 1

    @classmethod
    def get_number_of_plots(cls):
        return cls.number_of_plot

    def __del__(self):
        del self.canvas
        del self.legend

    def save(self, extension='pdf'):
        if self.canvas or not self.canvas.IsOnHeap():
            return
        self.canvas.Print(self.name + '.'+ extension)


    def add(self, obj, colour, opts=[], label=''):

        # if ',' in opts:
        #     colour, drawopts = opts.split(',')
        # else:
        #     colour, drawopts = opts, ''

        set_style(obj, colour)

        self.objects.append(obj)

        if self.opts:
            self.opts.extend(opts)
        else:
            self.opts.extend(opts)

        if not label:
            label = obj.GetName()
        self.labels.append(label)

    def dump(self):
        text = ''

        text += self.name + ' = ROOT.TCanvas("' + self.name + '", "' + self.name + '", 600, 600)\n'

        for obj, drawopts in zip(self.objects, self.opts):
            text += 'h_' + obj.GetName() + '.Draw("'+drawopts+'")\n'

            # (items_sel[k]->GetFile(), items_sel[k]->GetName(), items_sel[k]->GetText())
            # temp->SetDrawOptions(lnk->GetOption())
            # temp->SetColour(colours[k])
            # Int_t rebin = nentryRebin->GetIntNumber()
            # if(rebin > 1) temp->SetRebinNumber(nentryRebin->GetIntNumber())
            # if(checkNormalise->GetState() ) temp->SetScaleFactor(1/h->Integral())
            # if(checkNormalise2->GetState()) temp->SetScaleFactor(((TH1*)plot_list->At(0))->Integral()/h->Integral())
            # //        macro->AddHisto(temp)

        return text


    def compute_ranges(self):

        # ymax
        ymax = -1.e300
        for obj in self.objects:
            hmax = obj.GetMaximum()
            if hmax > ymax:
                ymax = hmax

        # ymin
        ymin = 1.e300
        for obj in self.objects:
            hmin = obj.GetMinimum()
            if hmin < ymin:
                ymin = hmin

        # xmax
        xmax = -1.e300
        for obj in self.objects:
            hmax = obj.GetXaxis().GetXmax()
            if hmax > xmax:
                xmax = hmax

        # xmin
        xmin = 1.e300
        for obj in self.objects:
            hmin = obj.GetXaxis().GetXmin()
            if hmin < xmin:
                xmin = hmin

        return xmin, xmax, ymin, ymax


    def create(self, logx=False, logy=False, do_ratio=False):

        # try to guess variable
        names = [ obj.GetName() for obj in self.objects ]

        variable = names[0] if names else ''

        if variable.startswith('h_'):
            variable = variable[2:]

        if variable not in plots_conf:
            vartmp = variable[:variable.find('[')]
            conf = plots_conf.get(vartmp, None)
        else:
            conf = plots_conf.get(variable, None)

        if conf is None:
            last = variable.split('_')[-1]

            if last in plots_conf:
                conf = plots_conf.get(last, None)

        if conf is None:
            conf = plots_conf['default']


        xtitle = conf.xtitle
        ytitle = conf.ytitle
        xmin   = conf.xmin
        xmax   = conf.xmax
        ymin = None
        ymax = None
        legpos = conf.legpos

        if xmin is None or xmax: ## is None or ymin is None or ymax is None:
            xmin, xmax, ymin, ymax = self.compute_ranges()

        if logy:
            ymin = 0.01

        self.canvas = ROOT.TCanvas(self.name, self.name, 800, 600)
        ROOT.SetOwnership(self.canvas, False)

        self.canvas.cd()

        if do_ratio:

            cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
            cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)

            cup.SetRightMargin(0.03)
            cup.SetBottomMargin(0.005)
            cup.SetLeftMargin(0.15)

            cdown.SetLeftMargin(0.15)
            cdown.SetRightMargin(0.03)
            cdown.SetBottomMargin(0.37)
            cdown.SetTopMargin(0.0054)

            cup.SetTickx()
            cup.SetTicky()
            cdown.SetTickx()
            cdown.SetTicky()
            cdown.SetFillColor(ROOT.kWhite)
            cup.Draw()
            cdown.Draw()

            if logy:
                cup.SetLogy()

        else:
            self.canvas.SetTicks()

            self.canvas.SetRightMargin(0.05)
            self.canvas.SetTopMargin(0.05)

            if logy:
                self.canvas.SetLogy()


        # configure histograms
        # for name, hist in bkg.iteritems():
        #     set_style(hist, color=colors_dict[name], fill=True)
        #     hist.SetLineColor(ROOT.kBlack)


        # stack
        #         # create SM stack
        # sm_stack = ROOT.THStack()

        # def _compare(a, b):
        #     amax = a.GetMaximum()
        #     bmax = b.GetMaximum()
        #     return cmp(int(amax), int(bmax))

        # for hist in sorted(bkg.itervalues(), _compare):
        #     sm_stack.Add(hist)

        # add entries to legend
        if do_ratio:
            legymin = 0.60
            legymax = 0.88

            if legpos == 'left':
                legxmin = 0.20
                legxmax = 0.53
            elif legpos == 'right':
                legxmin = 0.55
                legxmax = 0.91
        else:
            legymin = 0.80
            legymax = 0.94

            if legpos == 'left':
                legxmin = 0.20
                legxmax = 0.53
            elif legpos == 'right':
                legxmin = 0.65
                legxmax = 0.92

        self.legend = ROOT.TLegend(legxmin, legymin, legxmax, legymax)
        self.legend.SetBorderSize(0)
        self.legend.SetFillColor(0)

        for obj, label in zip(self.objects, self.labels):
            self.legend.AddEntry(obj, label)


        if do_ratio:
            cup.cd()

        # first histogram to configure
        print(self.objects)
        chist = self.objects[0]

        # Axis
        if xmin is not None and xmax is not None:
            chist.GetXaxis().SetRangeUser(xmin, xmax)
        if ymin is not None and ymax is not None:
            chist.GetYaxis().SetRangeUser(ymin, ymax)

        # if self.logy:
        #     chist.SetMaximum(ymax*1000)
        #     chist.SetMinimum(ymin)

        # Titles and labels
        if xtitle:
            if do_ratio:
                chist.GetXaxis().SetLabelSize(0.)
            else:
                chist.GetXaxis().SetTitle(xtitle)
                chist.GetXaxis().SetTitleOffset(1.20)

        if 'BIN' in ytitle:
            width = chist.GetBinWidth(1)

            if width > 10:
                ytitle = ytitle.replace('BIN', '{:.0f}'.format(width))
            else:
                ytitle = ytitle.replace('BIN', '{:.2f}'.format(width))

        chist.GetYaxis().SetTitle(ytitle)
        chist.GetYaxis().SetTitleOffset(1.2)

        # if data:
        # data_graph = make_poisson_cl_errors(data)

        # set_style(data_graph, msize=1, lwidth=2, color=ROOT.kBlack)

        #data_graph.Draw('P0Z')
        #data.Draw("P same")

        chist.Draw(self.opts[0])

        if do_ratio:
            cup.RedrawAxis()
        else:
            self.canvas.RedrawAxis()

        for obj, drawopts in zip(self.objects[1:], self.opts[1:]):
            obj.Draw(drawopts)

        if do_ratio:
            cup.RedrawAxis()
        else:
            self.canvas.RedrawAxis()

        self.legend.Draw()


    def draw_legend():

        if len(self.labels) == 1 or len(self.labels) != len(self.objects):
            return

        max_width = len(self.labels[0]) * 0.01
        max_height = len(self.labels) * 0.035

        xmax = 0.86
        ymax = 0.86
        ymin = ymax - max_height if (ymax - max_height)>0.2 else 0.2
        xmin = xmax - max_width  if (xmax - max_width) >0.2 else 0.2

        # Create and plot legend
        leg = ROOT.TLegend(xmin, ymin, xmax, ymax)
        leg.SetFillColor(0)

        for obj, lbl in zip(self.objects, self.labels):
            leg.AddEntry(obj, lbl)
        leg.Draw()
