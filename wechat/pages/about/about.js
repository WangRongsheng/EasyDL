//index.js
//获取应用实例
const app = getApp()

Page({
  data: {
  
  },
  onLoad: function () {
    
  },
  buttonClient1: function(){
    // console.log("点击了按钮");
    wx.navigateTo({
      url: '../label/label',
    })
  },
  buttonClient2: function(){
    // console.log("点击了按钮");
    wx.navigateTo({
      url: '../intro/intro',
    })
  },
  buttonClient3: function(){
    // console.log("点击了按钮");
    wx.navigateTo({
      url: '../use/use',
    })
  },
  buttonClient4: function(){
    // console.log("点击了按钮");
    wx.navigateTo({
      url: '../team/team',
    })
  },
  buttonClient5: function(){
    // console.log("点击了按钮");
    wx.navigateTo({
      url: '../contact/contact',
    })
  }
})
