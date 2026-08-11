******************************************************************
*  COPYBOOK  : GFMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : MT
******************************************************************
 01  RT-FMT-RATING.

          03 RT-FMT-TERRITORY-CODE            PIC X(3).
          03 RT-FMT-CLASS-CODE                PIC X(4).
          03 RT-FMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FMT-RATED-PREMIUM             PIC 9(9)V9(2).
