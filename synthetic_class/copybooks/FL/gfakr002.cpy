******************************************************************
*  COPYBOOK  : GFAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : AK
******************************************************************
 01  RT-FAK-RATING.

          03 RT-FAK-TERRITORY-CODE            PIC X(3).
          03 RT-FAK-CLASS-CODE                PIC X(4).
          03 RT-FAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FAK-RATED-PREMIUM             PIC 9(9)V9(2).
