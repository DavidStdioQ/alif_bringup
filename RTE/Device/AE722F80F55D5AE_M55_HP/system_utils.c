/* Copyright (C) 2022 Alif Semiconductor - All Rights Reserved.
 * Use, distribution and modification of this code is permitted under the
 * terms stated in the Alif Semiconductor Software License Agreement
 *
 * You should have received a copy of the Alif Semiconductor Software
 * License Agreement with this file. If not, please write to:
 * contact@alifsemi.com, or visit: https://alifsemi.com/license
 *
 */
/******************************************************************************
 * @file     system_utils.c
 * @author   Sudhir Sreedharan
 * @email    sudhir@alifsemi.com
 * @brief    System  Utility functions
 * @version  V1.0.0
 * @date     13. May 2021
 * @bug      None
 * @Note     None
 ******************************************************************************/
#include <system_utils.h>

/**
  \fn          void PMU_delay_loop_us(unsigned int delay_us)
  \brief       Using PMU cycle counter for delay. User need to
               take care of disabling the preemption before
	       calling this PMU_delay_loop_us function. Maximum
               delay supported (2^32/(SystemCoreClock/1000000))
               micro seconds.
  \param[in]   delay_us delay in micro seconds.
*/
void PMU_delay_loop_us(unsigned int delay_us)
{
    if (delay_us == 0)
            return;
    uint32_t timestamp = ARM_PMU_Get_CCNTR();
    unsigned int delay_in_cycles = delay_us * (GetSystemCoreClock()/1000000);
    unsigned int diff = 0, curt_count = 0;

    while (diff < delay_in_cycles)
    {
        curt_count = ARM_PMU_Get_CCNTR();
        if(curt_count > timestamp)
            diff = curt_count - timestamp;
        else
            diff = (((0xFFFFFFFF) - timestamp) + curt_count);
    }
}

/**
  \fn          void RTSS_IsGlobalCacheClean_Required (void)
  \brief       Return True if Global Cache Clean operation is required
  return       True : If CacheOperation Required, else False
*/
__attribute__ ((weak))
bool RTSS_IsGlobalCacheClean_Required (void)
{
    /*
     * This is a hook, where user can decide on Global Cache clean operation.
     *
     * If the system is not using any Cache writeback region in their
     * application, they can return false to skip the Global Cache Cleaning
     * completely.
     *
     */

    return true;
}

/**
  \fn          void RTSS_IsCacheClean_Required_by_Addr (volatile void *addr, int32_t size)
  \brief       Return True if Cache Clean operation is required for the provided
               address region else return False.
  \param[in]   addr    address
  \param[in]   size   size of memory block (in number of bytes)
  return       True : If CacheOperation Required, else False
*/
__attribute__ ((weak))
bool RTSS_IsCacheClean_Required_by_Addr (volatile void *addr, int32_t size)
{
    (void)size;
    /*
     * This is a hook, where user can redefine its implementation in application.
     *
     * For some scenarios, User don’t need to do anything apart from DSB for
     * un-cached or shared regions, and don’t need to clean write-through regions.
     * This particular API is introduced to reduce the overhead in Cache operation
     * function for the above scenarios mentioned.
     *
     * User can define the range of memories for the cache operations can be skipped.
     * Return True if cache operation is required else return False.
     *
     */

    /*
     * If the provided address is in TCM, then no cache operation is required
     */
    if(RTSS_Is_TCM_Addr(addr))
    {
        return false;
    }

    return true;
}

/**
  \fn          void RTSS_IsCacheInvalidate_Required_by_Addr (volatile void *addr, int32_t size)
  \brief       Return True if Cache Invalidate operation is required for the provided
               address region else return False.
  \param[in]   addr    address
  \param[in]   size   size of memory block (in number of bytes)
  return       True : If CacheOperation Required, else False
*/
__attribute__ ((weak))
bool RTSS_IsCacheInvalidate_Required_by_Addr (volatile void *addr, int32_t size)
{
    (void)size;
    /*
     * This is a hook, where user can redefine its implementation in application.
     *
     * For some scenarios, User don’t need to do anything apart from DSB for
     * un-cached or shared regions, and don’t need to clean write-through regions.
     * This particular API is introduced to reduce the overhead in Cache operation
     * function for the above scenarios mentioned.
     *
     * User can define the range of memories for the cache operations can be skipped.
     * Return True if cache operation is required else return False.
     *
     */

     /*
     * If the provided address is in TCM, then no cache operation is required
     */
    if(RTSS_Is_TCM_Addr(addr))
    {
        return false;
    }

    return true;
}
