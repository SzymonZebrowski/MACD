import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np


class Controller:
    def __init__(self, dataset):
        self.df = pd.read_csv(dataset)
        self.dates = self.df.iloc[:, 0].values
        self.closing_values = self.df.iloc[:, 4].values
        self.init_wallet()
        self.count = 1000

    def EMA(self, actual_sample, periods, data):
        one_minus_alpha = 1 - (2 / (periods-1))
        nominator = 0
        denominator = 0
        for i in range(0, periods):
            if actual_sample - i < 0:
                continue
            var = one_minus_alpha**i
            nominator += data[actual_sample - i]*var
            denominator += var
        return nominator/denominator

    def MACD(self, data):
        macd_list = []
        signal_list = []
        for i in range(0, 1000):
            ema_12 = self.EMA(i, 12, data)
            ema_26 = self.EMA(i, 26, data)
            macd = ema_12-ema_26
            macd_list.append(macd)
            ema_9 = self.EMA(i, 9, macd_list)
            signal_list.append(ema_9)

        return macd_list, signal_list

    def export_to_file(self, data, filename):
        file = open('data/'+filename, 'w')
        for x in data:
            file.write(str(x)+'\n')
        file.close()

    def ultimate_export(self, dates, closing_values, macd, signal, filename):
        file = open('data/' + filename, 'w')
        for x in range(len(dates)):
            file.write(str(dates[x]) + ',' + str(closing_values[x]) + ',' + str(macd[x]) + ',' + str(signal[x]) + '\n')
        file.close()

    def plot_graph(self, days):
        macd, signal = self.MACD(self.closing_values)
        macd = list(map(lambda x: x*1, macd))
        signal = list(map(lambda x: x*1, signal))

        macd = np.asarray(macd)
        signal = np.asarray(signal)

        plt.plot(np.arange(0, days), macd[:days], label='MACD', linewidth='3.0')
        plt.plot(np.arange(0, days), signal[:days], label='SIGNAL')
        #plt.plot(np.arange(0, days), self.closing_values[:days])

        idx = np.argwhere(np.diff(np.sign(macd[:days] - signal[:days]))).flatten()
        idx_sell = list(filter(lambda x: macd[x] > signal[x], idx))
        idx_buy = list(filter(lambda x: macd[x] < signal[x], idx))
        plt.plot(np.arange(0, days)[idx_sell], macd[idx_sell], 'ro', label='sell')
        plt.plot(np.arange(0, days)[idx_buy], macd[idx_buy], 'go', label='buy')
        plt.legend(loc='lower center')
        plt.show()

    def init_wallet(self):
        self.stock = 1000
        self.funds = 0

    def balance(self):
        print("Starting value: ", 1000 * self.closing_values[0])
        print("Final value: ", self.funds + self.stock*self.closing_values[999])
        print("Stock: ", self.stock)
        print("You've earned ", self.funds + self.stock*self.closing_values[999] - 1000 * self.closing_values[0])
        print("That's {0:5.3f}%".format((self.funds + self.stock*self.closing_values[999] - 1000 * self.closing_values[0])/(10*self.closing_values[0])))
        return (self.funds + self.stock*self.closing_values[999] - 1000 * self.closing_values[0])/(10*self.closing_values[0])

    def strategy_1(self):
        print("Strategy 1")
        macd, signal = self.MACD(self.closing_values)
        macd = np.asarray(macd)
        signal = np.asarray(signal)
        idx_sell = list(filter(lambda x: macd[x] > signal[x] and macd[x - 1] < signal[x - 1], range(1, 1000)))
        idx_buy = list(filter(lambda x: macd[x] < signal[x] and macd[x - 1] > signal[x - 1], range(1, 1000)))

        self.init_wallet()
        text = []
        for i in range(0, 1000):
            if i in idx_sell:
                self.funds += self.stock*self.closing_values[i]
                self.stock = 0
                text.append("{} S {}".format(i, self.closing_values[i]))
            elif i in idx_buy:
                self.stock += self.funds // self.closing_values[i]
                self.funds = 0
                text.append("{} B {}".format(i, self.closing_values[i]))

        self.balance()
        return text

ctr = Controller(os.getcwd()+'\data\wig20_d.csv')
#export_to_file(macd, 'wig20_macd.csv')
#export_to_file(signal, 'wig20_signal.csv')
#export_to_file(dates, 'wig20_dates.csv')
#export_to_file(closing_values, 'wig20_closing_values.csv')
#ultimate_export(dates, closing_values, macd, signal, 'wig20_ultimate.csv')

ctr.plot_graph(1000)
a = ctr.strategy_1()

