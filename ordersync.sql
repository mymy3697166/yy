/*
Navicat MySQL Data Transfer

Source Server         : mysql
Source Server Version : 50716
Source Host           : localhost:3306
Source Database       : ordersync

Target Server Type    : MYSQL
Target Server Version : 50716
File Encoding         : 65001

Date: 2016-11-10 13:34:36
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for fetchtime
-- ----------------------------
DROP TABLE IF EXISTS `fetchtime`;
CREATE TABLE `fetchtime` (
  `target` varchar(32) NOT NULL,
  `next_time` date NOT NULL,
  PRIMARY KEY (`target`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for meituanorder
-- ----------------------------
DROP TABLE IF EXISTS `meituanorder`;
CREATE TABLE `meituanorder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` bigint(11) DEFAULT NULL COMMENT '订单ID',
  `wm_order_id_view` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '订单展示ID',
  `app_poi_code` int(11) DEFAULT NULL COMMENT 'APP方商家ID',
  `wm_poi_name` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '美团商家名称',
  `wm_poi_address` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '美团商家地址',
  `wm_poi_phone` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '美团商家电话',
  `recipient_address` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '收件人地址',
  `recipient_phone` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '收件人电话',
  `recipient_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '收件人姓名',
  `recipient_gender` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '收件人性别',
  `shipping_fee` double DEFAULT NULL COMMENT '门店配送费',
  `total` double DEFAULT NULL COMMENT '总价',
  `original_price` double DEFAULT NULL COMMENT '原价',
  `caution` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '忌口或备注',
  `shipper_phone` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '送餐员电话',
  `status` int(11) DEFAULT NULL COMMENT '订单状态 订单当前状态code，详情请参考13.1节',
  `city_id` int(11) DEFAULT NULL COMMENT '城市ID(目前暂时用不到此信息)',
  `has_invoiced` int(11) DEFAULT NULL COMMENT '是否开发票',
  `invoice_title` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '发票抬头',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `utime` datetime DEFAULT NULL COMMENT '更新时间',
  `delivery_time` datetime DEFAULT NULL COMMENT '用户预计送达时间，“立即送达”时为0',
  `is_third_shipping` int(11) DEFAULT NULL COMMENT '是否是第三方配送平台配送（0否；1是） pay_type 支付类型（1货到付款；2在线支付）',
  `latitude` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT ' 实际送餐地址纬度',
  `longitude` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '实际送餐地址经度',
  `order_send_time` datetime DEFAULT NULL COMMENT '用户下单时间',
  `order_receive_time` datetime DEFAULT NULL COMMENT '143254561110 , 商户收到时间',
  `order_confirm_time` datetime DEFAULT NULL COMMENT '143254561110 , 商户确认时间',
  `order_cancel_time` datetime DEFAULT NULL COMMENT '143254562340, 订单取消时间',
  `order_completed_time` datetime DEFAULT NULL COMMENT ' 143254562340, 订单完成时间',
  `logistics_status` int(11) DEFAULT NULL COMMENT ' 20, 配送订单状态code，若is_mt_logistics不为1则此字段为空，详情请参考13.5.1节',
  `logistics_id` bigint(11) DEFAULT NULL COMMENT '7, 配送方ID，若is_mt_logistics不为1则此字段为空',
  `logistics_name` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '斑马快送, 配送方名称，若is_mt_logistics不为1则此字段为空',
  `logistics_send_time` datetime DEFAULT NULL COMMENT '143254562350, 配送单下单时间，若is_mt_logistics不为1则此字段为空',
  `logistics_confirm_time` datetime DEFAULT NULL COMMENT '143254561110 , 配送单确认时间，若is_mt_logistics不为1则此字段为空',
  `logistics_cancel_time` datetime DEFAULT NULL COMMENT '143254562340, 配送单取消时间，若is_mt_logistics不为1则此字段为空',
  `logistics_fetch_time` datetime DEFAULT NULL COMMENT '143254562340, 骑手取单时间，若is_mt_logistics不为1则此字段为空',
  `logistics_completed_time` datetime DEFAULT NULL COMMENT ' 143254562340, 配送单完成时间，若is_mt_logistics不为1则此字段为空',
  `logistics_dispatcher_name` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '143254562340, 骑手姓名，若is_mt_logistics不为1则此字段为空',
  `logistics_dispatcher_mobile` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT ' 143254562340, 骑手电话，若is_mt_logistics不为1则此字段为空',
  `distance` double(11,0) DEFAULT NULL COMMENT '收货人距店铺的距离（单位米）',
  `num` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '订单序号',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3634 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- ----------------------------
-- Table structure for meituanorderbackinfo
-- ----------------------------
DROP TABLE IF EXISTS `meituanorderbackinfo`;
CREATE TABLE `meituanorderbackinfo` (
  `id` int(11) NOT NULL,
  `order_id` bigint(11) DEFAULT NULL COMMENT '订单ID',
  `poi_id` bigint(11) DEFAULT NULL COMMENT '商铺ID',
  `apply_type` int(11) DEFAULT NULL COMMENT '申请类型',
  `apply_time_fmt` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '申请时间',
  `apply_reason` varchar(255) DEFAULT NULL COMMENT '申请原因说明',
  `res_type` int(11) DEFAULT NULL COMMENT '结果类型',
  `res_time_fmt` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '结果时间',
  `res_reason` varchar(255) DEFAULT NULL COMMENT '结果说明',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for meituanorderdetail
-- ----------------------------
DROP TABLE IF EXISTS `meituanorderdetail`;
CREATE TABLE `meituanorderdetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_id` bigint(11) DEFAULT NULL COMMENT 'id',
  `app_food_code` varchar(255) DEFAULT NULL COMMENT '食物编号',
  `food_name` varchar(255) DEFAULT NULL COMMENT '食物名称',
  `quantity` int(11) DEFAULT NULL COMMENT '量',
  `price` double DEFAULT NULL COMMENT '价格',
  `box_num` int(11) DEFAULT NULL COMMENT '盒数',
  `box_price` double DEFAULT NULL COMMENT '盒价格',
  `unit` varchar(255) DEFAULT NULL COMMENT '单位',
  `origin_price` double DEFAULT NULL COMMENT '折扣',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7438 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for meituanorderextras
-- ----------------------------
DROP TABLE IF EXISTS `meituanorderextras`;
CREATE TABLE `meituanorderextras` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `order_id` bigint(11) DEFAULT NULL COMMENT '订单ID',
  `fee` double(11,0) DEFAULT NULL COMMENT '活动优惠金额，是美团承担活动费用和商户承担活动费用的总和',
  `remark` varchar(255) DEFAULT NULL COMMENT '满10元减2.5元,（优惠说明）',
  `category` int(11) DEFAULT NULL COMMENT '活动类型',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7264 DEFAULT CHARSET=utf8mb4;
SET FOREIGN_KEY_CHECKS=1;
