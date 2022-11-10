#ifndef RANDOM_H
#define RANDOM_H


//thanks: https://stackoverflow.com/a/19036349
template<class T>
class Random {
public:
    Random() = default;
    Random(std::mt19937::result_type seed) : eng(seed) {}
    T DrawNumber(T min, T max){
        return std::uniform_int_distribution<T>{min, max}(eng);
    }

private:        
    std::mt19937 eng{std::random_device{}()};
};


#endif