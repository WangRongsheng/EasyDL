var app = getApp();
var api = require('../../utils/baiduai.js');
Page({
  data: {
    motto: 'EasyDL',
    result: [],
    images: {},
    img:'',
    base64img:''
  },
  onShareAppMessage: function () {
    return {
      title: 'EasyDL识农害小程序',
      path: '/pages/index/index',
      success: function (res) {
        if (res.errMsg == 'shareAppMessage:ok') {
          wx.showToast({
            title: '分享成功',
            icon: 'success',
            duration: 500
          });
        }
      },
      fail: function (res) {
        if (res.errMsg == 'shareAppMessage:fail cancel') {
          wx.showToast({
            title: '分享取消',
            icon: 'loading',
            duration: 500
          })
        }
      }
    }
  },
  clear: function (event) {
    console.info(event);
    wx.clearStorage();
  },
  //事件处理函数
  bindViewTap: function () {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  uploads: function () {
    var that = this
    wx.chooseImage({
      count: 1, // 默认9
      sizeType: ['compressed'], // 可以指定是原图还是压缩图，默认二者都有
      sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
      success: function (res) {
        // 返回选定照片的本地文件路径列表，tempFilePath可以作为img标签的src属性显示图片
        //console.log( res )
        if (res.tempFiles[0].size > 4096 * 1024) {
          wx.showToast({
            title: '图片文件过大哦',
            icon: 'none',
            mask: true,
            duration: 1500
          })
        }else{
          that.setData({
            img: res.tempFilePaths[0]
          })
        }
        wx.showLoading({
            title: "分析中...",
            mask: true
        })
        //根据上传的图片读取图片的base64
        var fs = wx.getFileSystemManager();
        fs.readFile({
          filePath: res.tempFilePaths[0].toString(),
          encoding:'base64',
          success(res){
            //获取到图片的base64 进行请求接口
            api.easyDLRequest(res.data,6,{
                success(res){
                  console.info(typeof (res.error_code) == "undefined");
                  if (typeof (res.error_code) != "undefined") {
                    wx.hideLoading();
                    wx.showModal({
                      showCancel: false,
                      title: '错误码:' + res.error_code,
                      content: '错误信息:' + res.error_msg
                    })
                  }else{
                    if (res.results.length > 0) {
                      wx.hideLoading();
                      let dataList = res.results;
                      //暂时对置信度的值不处理。不太清楚JS如何处理超级大的负数
                      // dataList.forEach((item) => {
                      //   var num = new Number(item.score);
                      //   console.info(num)
                      //   item.score = num.toString().substring(0,5);
                      // })
                      that.setData({
                        result: dataList
                      })
                    }else{
                        wx.hideLoading();
                        wx.showModal({
                          showCancel: false,
                          title: '温馨提示',
                          content: '貌似没有识别出结果'
                        })
                    }
                  }
                }
            })
          }
        })
      },
    })
  },
  onLoad: function () {
  }
});