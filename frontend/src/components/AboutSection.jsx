import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Users, Star, Award } from 'lucide-react';
import banner2 from '../assets/banner2.png';

const AboutSection = () => {
  const features = [
    {
      icon: BookOpen,
      title: '经典传承',
      description: '深入研习《鬼谷子》《易经》等国学经典'
    },
    {
      icon: Users,
      title: '名师指导',
      description: '汇聚国学大师，传授正宗文化精髓'
    },
    {
      icon: Star,
      title: '智慧应用',
      description: '古典智慧与现代科技的完美结合'
    },
    {
      icon: Award,
      title: '品质保证',
      description: '因材施教的课程，系统化学习体系'
    }
  ];

  return (
    <div className="grid lg:grid-cols-2 gap-12 items-center">
      <div>
        <p className="text-lg text-gray-300 leading-relaxed mb-8">
          鬼谷子，纵横捭阖之祖，道家兵家之师，智慧谋略的化身。我们致力于传承鬼谷子文化精髓的传承，
          融合现代教育技术，构建线上国学教育新形态。在这里，古老的智慧与现代的思维碰撞，
          为您开启一扇通往智慧人生的大门。
        </p>
        
        <div className="grid sm:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="card-hover bg-gray-800/50 p-6 rounded-lg border border-gray-700"
            >
              <feature.icon className="w-8 h-8 text-gray-400 mb-3" />
              <h3 className="text-white font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
      
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
        className="relative"
      >
        <img 
          src={banner2} 
          alt="八卦星象图" 
          className="w-full rounded-lg shadow-2xl"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent rounded-lg" />
      </motion.div>
    </div>
  );
};

export default AboutSection;

