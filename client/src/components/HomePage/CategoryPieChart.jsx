import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { StyleSheet, Text, SafeAreaView, View, Dimensions } from 'react-native';
import { VictoryPie, VictoryLabel } from 'victory-native';
import { MONTHS } from '../../utils/constants';
import { theme } from '../../../theme';
import { formatNumber } from '../../utils/formatters';

const sampleData = [
  { x: 'Category 1', y: 1001.25, color: theme.gradient[0] },
  { x: 'Category 2', y: 2040, color: theme.gradient[1] },
  { x: 'Category 3', y: 3300, color: theme.gradient[2] },
  { x: 'Category 4', y: 4000.2, color: theme.gradient[3] },
  { x: 'Category 5', y: 5000, color: theme.gradient[4] },
  { x: 'Category 6', y: 1200.4, color: theme.gradient[5] },
  { x: 'Amount Left', y: 3400.6, color: theme.colors.white },
];

const getMonth = () => {
  const d = new Date();
  return MONTHS[d.getMonth()];
};

const CategoryPieChart = () => {
  const windowWidth = Dimensions.get('window').width;
  const pieRadius = windowWidth / 4;

  const [categoryBudgetData, setCategoryBudgetData] = useState([]);
  useEffect(() => {
    const d = new Date();
    axios
      .get('https://money-manager-dev.herokuapp.com/budget/category/all', {
        params: {
          month: d.getMonth() + 1,
          year: d.getFullYear(),
        },
      })
      .then((res) => {
        setCategoryBudgetData(res.data);
      })
      .catch((e) => console.error(e));
  }, []);

  const calculateExpense = {
    total: categoryBudgetData.reduce((acc, item) => {
      return acc + item.spent;
    }, 0),
  };
  const calculateBudget = {
    total: categoryBudgetData.reduce((acc, item) => {
      return acc + item.value;
    }, 0),
  };
  const ratio = `${Math.round((calculateExpense.total / calculateBudget.total) * 100)}%`;

  const categoryData = categoryBudgetData.map((category, index) => ({
    ...category,
    color: theme.gradient[index],
  }));

  categoryData.push({
    _id: toString(Math.random()),
    value: 0,
    spent: Math.round(calculateBudget.total - calculateExpense.total),
    category: 'Amount Left',
    color: theme.colors.white,
  });

  return (
    <SafeAreaView style={styles.centeredView}>
      <Text style={styles.title}>{getMonth()}&apos;s Spending</Text>
      <VictoryPie
        radius={pieRadius}
        innerRadius={pieRadius - pieRadius / 3}
        data={categoryData}
        x="category"
        y={(data) => data.spent}
        colorScale={theme.gradient.slice(0, categoryData.length - 1).concat([theme.colors.white])}
        labels={() => null}
        style={{
          parent: {
            marginVertical: -pieRadius,
            alignSelf: 'center',
          },
          data: {
            stroke: theme.colors.grey,
            strokeWidth: 1,
          },
        }}
        labelComponent={
          <VictoryLabel
            textAnchor="middle"
            verticalAnchor="middle"
            x={windowWidth / 2}
            y={windowWidth / 2 + pieRadius / 7}
            style={[styles.labelMaj, styles.labelMin]}
            text={[`$${formatNumber(calculateExpense.total, 0)}`, `Spent in ${getMonth()}`]}
          />
        }
      />
      <View style={styles.pbar} key="pbar">
        <View
          style={[
            StyleSheet.absoluteFill,
            { backgroundColor: theme.colors.green, borderRadius: 20, width: ratio },
          ]}>
          <Text style={styles.pbarTextExpense}>{ratio}</Text>
        </View>
        <Text style={[styles.pbarTextBudget]}>${formatNumber(calculateBudget.total, 0)}</Text>
      </View>
      <View style={styles.categoryView}>
        {categoryData.map((item, index) => {
          return (
            <View
              style={[
                styles.card,
                {
                  backgroundColor: item.color,
                  borderBottomLeftRadius: index === categoryData.length - 1 ? 10 : 0,
                  borderBottomRightRadius: index === categoryData.length - 1 ? 10 : 0,
                  borderBottomWidth: index === categoryData.length - 1 ? 0 : 1,
                },
              ]}
              key={item._id}>
              <Text style={styles.cardText}>{item.category}</Text>
              <Text style={styles.cardText}>${formatNumber(item.spent)}</Text>
            </View>
          );
        })}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  centeredView: {
    display: 'flex',
    justifyContent: 'center',
    margin: 20,
    borderWidth: 4,
    borderRadius: 10,
    borderColor: theme.colors.primaryDark,
    paddingBottom: 50,
  },
  title: {
    alignSelf: 'center',
    fontSize: 30,
    fontWeight: 'bold',
    paddingVertical: 20,
    color: theme.colors.primary,
  },
  labelMaj: {
    fontSize: 30,
    fontFamily: '',
    color: theme.colors.primary,
    fontWeight: '600',
  },
  labelMin: {
    fontSize: 12,
    fontFamily: '',
    color: theme.colors.primary,
    fontWeight: '400',
  },
  pbar: {
    height: 30,
    width: '80%',
    marginTop: 20,
    marginHorizontal: 10,
    borderRadius: 20,
    borderColor: theme.colors.green,
    backgroundColor: theme.colors.white,
    flexDirection: 'row',
    justifyContent: 'flex-start',
    alignSelf: 'center',
  },
  pbarTextExpense: {
    fontSize: 18,
    fontWeight: '600',
    position: 'absolute',
    top: 4,
    left: 10,
  },
  pbarTextBudget: {
    fontSize: 18,
    fontWeight: '600',
    position: 'absolute',
    right: 10,
    top: 4,
  },
  categoryView: {
    marginTop: 15,
  },
  card: {
    borderBottomColor: theme.colors.grey,
    paddingVertical: 5,
    paddingHorizontal: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  cardText: {
    fontSize: 16,
    fontWeight: '600',
  },
});

export default CategoryPieChart;
